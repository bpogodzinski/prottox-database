import pandas as pd
from tqdm import tqdm
import re
import numpy as np
from scipy import stats

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from prottox.models import *

import sys
from pprint import pprint as pp

def calculate_percentile(data):
    arr = np.array(data)
    return stats.rankdata(arr, "average") / len(arr)


class Command(BaseCommand):
    # ONE TIME USE CODE
    # JUST TO POPULATE DATABASE
    help = 'Populate the database with csv file'
    ACTIVE_FACTOR_OFFSET = 14
    F1_TYPE_INDEX=11
    toxinRE = re.compile(r'([A-Za-z]{3})([0-9]+)([A-Z])([a-z])(\d+)?')
    factorsCreated = 0
    researchCreated = 0
    taxInfo = pd.read_csv(r'/home/panda/Dokumenty/Development/licencjat/data/taksonomia.csv', sep=';', header=0, index_col=0)



    def handle(self, *args, **options):
        data = pd.read_csv(r'/home/panda/Dokumenty/Development/licencjat/data/data.csv', sep=';', header=0, dtype=str)

        SF_list = []
        print('Created dataframe, calculating percentiles...')
        for index, row in tqdm(data.iterrows(), total=len(data.index)):
            if (pd.notnull(row['LC synergism factor (SF)'])) and (row['Interaction [SYN/IND/ANT](statistically significant)'] != 'IND'):
                try:
                    sf = float(row['LC synergism factor (SF)'].replace(',','.'))
                except ValueError:
                    continue
                SF_list.append(tuple([index, row['Interaction [SYN/IND/ANT](statistically significant)'], sf]))

        syn_list = [[x[0], x[2]] for x in SF_list if x[1] == 'SYN']
        ant_list = [[x[0], x[2]] for x in SF_list if x[1] == 'ANT']
        
        percentile_syn_list = calculate_percentile([x[1] for x in syn_list])*100
        percentile_ant_list = 100-(calculate_percentile([x[1] for x in ant_list])*100)
        
        for index in range(len(syn_list)):
            syn_list[index][1] = percentile_syn_list[index]
        for index in range(len(ant_list)):
            ant_list[index][1] = percentile_ant_list[index]

        complete_list = syn_list+ant_list

        SF_dict = {index:percentile for index, percentile in complete_list}

        antiduplicate_set = set()
        print('Beginning to populate ...')
        for index, row in tqdm(data.iterrows(), total=len(data.index)):
            factors = self.make_active_factor(row)
            target = self.createTargetSpecies(row["Target species"], row['Target developmental stage'], row['Target species strain'], row['Recognised resistance in target species'])
            publication = self.make_publication(row['AUTHORS'], row['PMID (PubMed ID)'], row['Link (if PMID not available)'], row['PUBLICATION DATE'])
            toxin_distrib = self.make_toxin_distrib(row['Toxin distribution'])
            quantity = None if pd.isnull(row['Proportion_F 1']) else self.createToxinQuantity(row['Proportion_F 1':'Proportion_F 8'], row['Proportion unit'])
            results = self.createResults(row['BIOASSAY TYPE':'Interaction estimation method'], index, SF_dict)
            label = row['Label']
            immutable_row = tuple([value for _, value in row.items()])
            if immutable_row not in antiduplicate_set:
                toxin_research = Toxin_research.objects.create(publication=publication, target=target, days_of_observation=row['Bioassay duration'], toxin_distribution=toxin_distrib, quantity=quantity, results=results, label=label)
                toxin_research.toxin.add(*factors)
                self.researchCreated += 1
                antiduplicate_set.add(immutable_row)
            # try:
            #     Toxin_research.objects.get(toxin__in=factors, publication=publication, target=target, days_of_observation=row['Bioassay duration'], toxin_distribution=toxin_distrib, quantity=quantity, results=results, label=label)
            # except ObjectDoesNotExist:
            #     toxin_research = Toxin_research.objects.create(publication=publication, target=target, days_of_observation=row['Bioassay duration'], toxin_distribution=toxin_distrib, quantity=quantity, results=results, label=label)
            #     toxin_research.toxin.add(*factors)
            #     self.researchCreated += 1
            # except MultipleObjectsReturned:
            #     toxin_research = Toxin_research.objects.filter(toxin__in=factors, publication=publication, target=target, days_of_observation=row['Bioassay duration'], toxin_distribution=toxin_distrib, quantity=quantity, results=results, label=label)
            #     primaryKey = toxin_research[0].pk
            #     assert all(toxinRes.pk == primaryKey for toxinRes in toxin_research), "Something went really wrong...(different PK)"


        print(f'Created {self.factorsCreated} new Factors!')
        print(f'Created {self.researchCreated} new Researches!')

    def make_active_factor(self,row):
        factors = []
        offset = 0
        while pd.notna(row.iloc[self.F1_TYPE_INDEX + offset]):
            last_rank, is_toxin = self.createRanks(row, offset)
            display_name = row.iloc[self.F1_TYPE_INDEX + offset - 1]
            NCBI_acc = '' if pd.isna(row.iloc[self.F1_TYPE_INDEX + offset + 5]) else row.iloc[self.F1_TYPE_INDEX + offset + 5]
            factor_source, cre = Factor_source.objects.get_or_create(source=row.iloc[self.F1_TYPE_INDEX + offset + 6]) if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + 6]) else (None,None)
            factor_isolation_source, cre = Factor_isolation_source.objects.get_or_create(isolation_source=row.iloc[self.F1_TYPE_INDEX + offset + 7]) if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + 7]) else (None,None)
            factor_form, cre = Factor_form.objects.get_or_create(form=row.iloc[self.F1_TYPE_INDEX + offset + 8]) if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + 8]) else (None,None)
            modification = row.iloc[self.F1_TYPE_INDEX + offset + 9] if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + 9]) else ''
            expression_host, cre = Factor_expression_host.objects.get_or_create(host=row.iloc[self.F1_TYPE_INDEX + offset + 10]) if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + 10]) else (None,None)
            kda = row.iloc[self.F1_TYPE_INDEX + offset + 11] if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + 11]) else None
            kda = float(kda.replace(',','.')) if type(kda) == str else kda
            prep = row.iloc[self.F1_TYPE_INDEX + offset + 12] if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + 12]) else ''
            chimeric = True if type(last_rank) is tuple else False

            taxonomyIterable = last_rank if chimeric else [last_rank]

            try:
                active_factor = Active_factor.objects.get(display_name=display_name, is_toxin=is_toxin, NCBI_accession_number=NCBI_acc, factor_source=factor_source, isolation_source=factor_isolation_source, factor_form=factor_form, modification_description=modification, 
                factor_expression_host=expression_host, kDa=kda, preparation=prep, is_chimeric=chimeric, taxonomy__in=taxonomyIterable)
            except ObjectDoesNotExist:
                active_factor = Active_factor.objects.create(display_name=display_name, is_toxin=is_toxin, NCBI_accession_number=NCBI_acc, factor_source=factor_source, isolation_source=factor_isolation_source, factor_form=factor_form, modification_description=modification, 
                factor_expression_host=expression_host, kDa=kda, preparation=prep, is_chimeric=chimeric)
                self.factorsCreated += 1

            except MultipleObjectsReturned:
                #Chimeric proteins have both last ranks so get returns same chimeric protein twice
                chimerics = Active_factor.objects.filter(display_name=display_name, is_toxin=is_toxin, NCBI_accession_number=NCBI_acc, factor_source=factor_source, isolation_source=factor_isolation_source, factor_form=factor_form, modification_description=modification, 
                factor_expression_host=expression_host, kDa=kda, preparation=prep, is_chimeric=chimeric, taxonomy__in=taxonomyIterable)
                #Just to be sure...
                primaryKey = chimerics[0].pk
                assert chimeric, "Something went relly wrong...(not chimeric)"
                assert all(toxin.pk == primaryKey for toxin in chimerics), "Something went really wrong...(different PK)"
                active_factor = chimerics[0]

            active_factor.taxonomy.add(*taxonomyIterable)
            factors.append(active_factor)
            offset += self.ACTIVE_FACTOR_OFFSET
        return factors

    def createRanks(self,row, offset):
        toxin = None
        last_rank = None
        r1 = row.iloc[self.F1_TYPE_INDEX + offset]
        if r1 == "chimeric protein":
            toxin = True
            last_rank1 = None
            last_rank2 = None
            firstTox = self.toxinRE.match(row.iloc[self.F1_TYPE_INDEX + offset + 1])
            if firstTox is None:
                last_rank1, created = FactorTaxonomy.objects.get_or_create(name=row.iloc[self.F1_TYPE_INDEX + offset + 1], parent=None)
            else:
                firstTox = firstTox.groups()
                firstTox = [x for x in firstTox if x is not None]
                
                last_rank1, created = FactorTaxonomy.objects.get_or_create(name=firstTox[0], parent=None)
                for i in range(1,len(firstTox)):
                    last_rank1, created = FactorTaxonomy.objects.get_or_create(name=firstTox[i], parent=last_rank1)
            
            secondTox = self.toxinRE.match(row.iloc[self.F1_TYPE_INDEX + offset + 2])
            if secondTox is None:
                last_rank2, created = FactorTaxonomy.objects.get_or_create(name=row.iloc[self.F1_TYPE_INDEX + offset + 2])
            else:
                secondTox = secondTox.groups()
                secondTox = [x for x in secondTox if x is not None]

                last_rank2, created = FactorTaxonomy.objects.get_or_create(name=secondTox[0], parent=None)
                for i in range(1,len(secondTox)):
                    last_rank2, created = FactorTaxonomy.objects.get_or_create(name=secondTox[i], parent=last_rank2)

            return (last_rank1, last_rank2), toxin
        elif r1 == "chemical pesticides":
            toxin = False
            typ, _ = FactorTaxonomy.objects.get_or_create(name=r1, parent=None)
            last_rank, _ = FactorTaxonomy.objects.get_or_create(name=row.iloc[self.F1_TYPE_INDEX + offset + 1], parent=typ)
            last_rank, _ = FactorTaxonomy.objects.get_or_create(name=row.iloc[self.F1_TYPE_INDEX + offset + 2], parent=last_rank)
            return last_rank, toxin
        else:
            toxin = True if len(r1) == 3 else False
            typ, created = FactorTaxonomy.objects.get_or_create(name=r1, parent=None)
            last_rank = typ
            for i in range(1,5):
                if pd.notna(row.iloc[self.F1_TYPE_INDEX + offset + i]):
                    rank, created = FactorTaxonomy.objects.get_or_create(name=row.iloc[self.F1_TYPE_INDEX + offset + i], parent=last_rank)
                    last_rank = rank
                else:
                    break
            return last_rank, toxin

    def createTargetSpecies(self, species, larvaeStage, targetStrain, toxinResistance):
        try:
            targetSpecies = SpeciesTaxonomy.objects.get(name=species)
        except ObjectDoesNotExist:
            targetInfo = self.taxInfo.loc[species]
            phylum = SpeciesTaxonomy.objects.get_or_create(name=targetInfo["Phylum"], taxID=targetInfo["Phylum ID"] if targetInfo["Phylum ID"] != 'xxx' else None, parent=None, taxonomy_rank=SpeciesTaxonomyRank.objects.get_or_create(name='Phylum')[0])[0]
            order = SpeciesTaxonomy.objects.get_or_create(name=targetInfo["Order"], taxID=targetInfo["Order ID"] if targetInfo["Order ID"] != 'xxx' else None, parent=phylum, taxonomy_rank=SpeciesTaxonomyRank.objects.get_or_create(name='Order')[0])[0]
            family = SpeciesTaxonomy.objects.get_or_create(name=targetInfo["Family"], taxID=targetInfo["Family ID"] if targetInfo["Family ID"] != 'xxx' else None, parent=order, taxonomy_rank=SpeciesTaxonomyRank.objects.get_or_create(name='Family')[0])[0]
            targetSpecies = SpeciesTaxonomy.objects.get_or_create(name=species, taxID=targetInfo["Target ID"] if targetInfo["Target ID"] != 'xxx' else None, parent=family, taxonomy_rank=SpeciesTaxonomyRank.objects.get_or_create(name='Species')[0])[0]

        stage = Larvae_stage.objects.get_or_create(stage=larvaeStage)[0]
        strain = TargetSpeciesStrain.objects.get_or_create(strain=targetStrain)[0] if pd.notnull(targetStrain) else None
        factors = toxinResistance if pd.notnull(toxinResistance) else None
        target = Target.objects.get_or_create(target_organism_taxonomy=targetSpecies, larvae_stage=stage, target_species_strain=strain, factor_resistance=factors)[0]
        return target

    def make_publication(self, author, pmid, link, date):
        pmid = '' if pd.isna(pmid) else int(pmid)
        link = '' if pd.isna(link) else link
        date = str(date)+'-01-01'
        author = self.make_author(author)
        try:
            pub = Publication.objects.get(article_link=link, pubmed_id=pmid, date=date, authors=author)
        except ObjectDoesNotExist:
            pub = Publication.objects.create(article_link=link, pubmed_id=pmid, date=date)
            pub.authors.add(author)
        return pub
    
    def make_author(self, surname):
        author, created = Author.objects.get_or_create(surname=surname)
        return author

    def make_toxin_distrib(self, distrib):
        toxin, created = Toxin_distribution.objects.get_or_create(distribution_choice=distrib)
        return toxin

    def createToxinQuantity(self, proportions, proportionUnit):
        value = ''
        measurement = ''
        unit = None
        if proportions[0] == 'reference':
            value = 'reference'
        else:
            value = ':'.join(proportions.dropna())
            unit, measurement = self.createMeasurementUnit(proportionUnit)

        return Toxin_quantity.objects.get_or_create(values=value, units=unit, measurement_type=measurement)[0]

    def createMeasurementUnit(self, proportionUnit):
        if pd.notna(proportionUnit):
            measurement = 'Weight/Area'
            unit = proportionUnit
        else:
            measurement = 'Proportion'
            unit = None
        
        return unit, measurement
   
    def createResults(self, resultRow, index, sf_dict):
        bio_type = Bioassay_type.objects.get_or_create(bioassay_type=resultRow['BIOASSAY TYPE'])[0]
        bio_result = resultRow['BIOASSAY RESULT OBSERVED']
        lcMIN = '' if pd.isna(resultRow['LC (FL95 lower)']) else resultRow['LC (FL95 lower)']
        lcMAX = '' if pd.isna(resultRow['LC (FL95 upper)']) else resultRow['LC (FL95 upper)']
        unit = '' if pd.isna(resultRow['Bioassay result unit']) else resultRow['Bioassay result unit']
        slLC = '' if pd.isna(resultRow['Slope (b) (LC)']) else resultRow['Slope (b) (LC)']
        slSE = '' if pd.isna(resultRow['Slope (b) Standard error (LC)']) else resultRow['Slope (b) Standard error (LC)']
        chisq = '' if pd.isna(resultRow['Chi-square']) else resultRow['Chi-square']
        bio_expected = '' if pd.isna(resultRow['BIOASSAY RESULT EXPECTED']) else resultRow['BIOASSAY RESULT EXPECTED']
        interaction = '' if pd.isna(resultRow['Interaction [SYN/IND/ANT](statistically significant)']) else resultRow['Interaction [SYN/IND/ANT](statistically significant)']
        syn_factor = '' if pd.isna(resultRow['LC synergism factor (SF)']) else resultRow['LC synergism factor (SF)']
        ant_factor = '' if pd.isna(resultRow['LC antagonism factor (AF)']) else resultRow['LC antagonism factor (AF)']
        est_method = '' if pd.isna(resultRow['Interaction estimation method']) else resultRow['Interaction estimation method']
        percentile = sf_dict.get(index, None)

        return Result.objects.get_or_create(percentile=percentile, bioassay_type=bio_type, bioassay_result=bio_result, bioassay_unit=unit, LC95min=lcMIN, LC95max=lcMAX, expected=bio_expected, interaction=interaction, synergism_factor=syn_factor, antagonism_factor=ant_factor, estimation_method=est_method, slopeLC=slLC, slopeSE=slSE, chi_square=chisq)[0]

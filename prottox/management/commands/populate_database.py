import pandas as pd
from tqdm import tqdm
import re

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from prottox.models import *

class Command(BaseCommand):

    help = 'Populate the database with csv file'
    ACTIVE_FACTOR_OFFSET = 14
    F1_TYPE_INDEX=11
    toxinRE = re.compile(r'([A-Za-z]{3})([0-9]+)([A-Z])([a-z])(\d+)?')
    factorsCreated = 0

    def handle(self, *args, **options):
        info = '[INFO] {}'
        warn = '[WARNING] {}'
        data = pd.read_csv('/home/panda/Dokumenty/Development/licencjat/data/data.csv', sep=';', header=0, dtype=str)
        taxInfo = pd.read_csv('/home/panda/Dokumenty/Development/licencjat/data/taksonomia.csv', sep=';', header=0)
        print(info.format('Created dataframe. Begin to populate ...'))
        for index, row in tqdm(data.iterrows(), total=len(data.index)):
            self.make_active_factor(row)
            
        print(info.format(f'Created {self.factorsCreated} new Factors!'))

    def make_active_factor(self,row):
        offset = 0
        while pd.notna(row.iloc[self.F1_TYPE_INDEX + offset]):
            last_rank, is_toxin = self.createRanks(row, offset)
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
                active_factor = Active_factor.objects.get(is_toxin=is_toxin, NCBI_accession_number=NCBI_acc, factor_source=factor_source, isolation_source=factor_isolation_source, factor_form=factor_form, modification_description=modification, 
                factor_expression_host=expression_host, kDa=kda, preparation=prep, is_chimeric=chimeric, taxonomy__in=taxonomyIterable)
            except ObjectDoesNotExist:
                active_factor = Active_factor.objects.create(is_toxin=is_toxin, NCBI_accession_number=NCBI_acc, factor_source=factor_source, isolation_source=factor_isolation_source, factor_form=factor_form, modification_description=modification, 
                factor_expression_host=expression_host, kDa=kda, preparation=prep, is_chimeric=chimeric)
                self.factorsCreated += 1
            except MultipleObjectsReturned:
                #Chimeric proteins have both last ranks so get returns same chimeric protein twice
                chimerics = Active_factor.objects.filter(is_toxin=is_toxin, NCBI_accession_number=NCBI_acc, factor_source=factor_source, isolation_source=factor_isolation_source, factor_form=factor_form, modification_description=modification, 
                factor_expression_host=expression_host, kDa=kda, preparation=prep, is_chimeric=chimeric, taxonomy__in=taxonomyIterable)
                #Just to be sure...
                primaryKey = chimerics[0].pk
                assert chimeric, "Something went relly wrong...(not chimeric)"
                assert all(toxin.pk == primaryKey for toxin in chimerics), "Something went really wrong...(different PK)"
                active_factor = chimerics[0]

            active_factor.taxonomy.add(*taxonomyIterable)
            offset += self.ACTIVE_FACTOR_OFFSET


                


    def createRanks(self,row, offset):
        toxin = None
        last_rank = None
        r1 = row.iloc[self.F1_TYPE_INDEX + offset]
        if r1 == "chimeric protein":
            toxin = True
            last_rank1 = None
            last_rank2 = None
            firstTox = self.toxinRE.match(row.iloc[self.F1_TYPE_INDEX + offset + 1]).groups()
            secondTox = self.toxinRE.match(row.iloc[self.F1_TYPE_INDEX + offset + 2]).groups()
            firstTox = [x for x in firstTox if x is not None]
            secondTox = [x for x in secondTox if x is not None]

            last_rank1, created = FactorTaxonomy.objects.get_or_create(name=firstTox[0], parent=None)
            for i in range(1,len(firstTox)):
                last_rank1, created = FactorTaxonomy.objects.get_or_create(name=firstTox[i], parent=last_rank1)
            
            last_rank2, created = FactorTaxonomy.objects.get_or_create(name=secondTox[0], parent=None)
            for i in range(1,len(secondTox)):
                last_rank2, created = FactorTaxonomy.objects.get_or_create(name=secondTox[i], parent=last_rank2)
            return (last_rank1, last_rank2), toxin
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


    # def make_author(self, name):
    #     author, created = Author.objects.get_or_create(surname= name)
    #     return author

    # def make_publication(self, author, pmid, link, date):
    #     pmid = '' if pd.isna(pmid) else int(pmid)
    #     link = '' if pd.isna(link) else link
    #     date = str(date)+'-01-01'
    #     pub, created = Publication.objects.get_or_create(article_link=link, pubmed_id=pmid, date=date)
    #     if created:
    #         pub.authors.add(author)
    #     return pub

    # def make_toxin_distrib(self,choice):
    #     translate = {
    #         'Surface contamination':'SC',
    #         'Diet incorporation':'DI',
    #         'Force feeding':'FF',
    #         'Droplet feeding':'DF',
    #     }
    #     toxin, created = Toxin_distribution.objects.get_or_create(distribution_choice=translate[choice])
    #     return toxin
            




        

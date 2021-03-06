import re

from django.db import models

class SpeciesTaxonomyRank(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SpeciesTaxonomy(models.Model):
    taxID = models.PositiveIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    taxonomy_rank = models.ForeignKey(SpeciesTaxonomyRank, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class FactorTaxonomy(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    @property
    def fullname(self):
        taxList = []
        taxList.append(self.name)
        parent = self.parent
        while parent is not None:
            taxList.append(parent.name)
            parent = parent.parent
        
        taxList = list(reversed(taxList))
        name = "".join(taxList)
        pattern = re.compile(r'^[A-Za-z]{3}[0-9A-Z]+[A-Z]*[a-z]*[\d]*$')

        return name if pattern.match(name) else taxList[-1]
        

    def __str__(self):
        return self.fullname


class Author(models.Model):
    name = models.CharField(max_length=50, blank=True)
    surname = models.CharField(max_length=50)

    @property
    def fullname(self):
        return f"{self.name} {self.surname}" if self.name else f"{self.surname}"

    def __str__(self):
        return self.fullname


class Factor_form(models.Model):
    form = models.CharField(max_length=30)

    def __str__(self):
        return self.form


class Publication(models.Model):
    date = models.DateField()
    authors = models.ManyToManyField(Author)
    pubmed_id = models.CharField(max_length=50, blank=True)
    article_link = models.CharField(max_length=200, blank=True)

    @property
    def publicationInfo(self):
        allAuthors = self.allAuthors
        info=''

        if self.pubmed_id:
            info = f"PubMed ID: {self.pubmed_id}"
        elif self.article_link:
            info = f"Article link: {self.article_link}"

        return f"{self.date.year} {allAuthors} {info}"

    @property
    def allAuthors(self):
        return ", ".join(sorted([author.fullname for author in self.authors.all()]))

    def __str__(self):
        return self.publicationInfo

    @property
    def link(self):
        PUBMED_LINK_TEMPLATE = "https://www.ncbi.nlm.nih.gov/pubmed/{ID}"
        if self.pubmed_id:
            return PUBMED_LINK_TEMPLATE.format(ID=self.pubmed_id)
        elif self.article_link:
            return self.article_link
        else:
            return None

class Factor_source(models.Model):
    source = models.CharField(max_length=50)

    def __str__(self):
        return self.source


class Factor_isolation_source(models.Model):
    isolation_source = models.CharField(max_length=40)

    def __str__(self):
        return self.isolation_source


class Factor_expression_host(models.Model):
    host = models.CharField(max_length=40)

    def __str__(self):
        return self.host


class Active_factor(models.Model):
    display_name = models.CharField(max_length=100, blank=True)
    is_toxin = models.BooleanField(null=False, blank=False, default=True)
    factor_source = models.ForeignKey(Factor_source, on_delete=models.CASCADE, blank=True, null=True)
    NCBI_accession_number = models.CharField(max_length=20, blank=True)
    factor_form = models.ForeignKey(Factor_form, on_delete=models.CASCADE, blank=True, null=True)
    isolation_source = models.ForeignKey(
        Factor_isolation_source, on_delete=models.CASCADE, blank=True, null=True)
    modification_description = models.TextField(blank=True)
    factor_expression_host = models.ForeignKey(
        Factor_expression_host, on_delete=models.CASCADE, blank=True, null=True)
    is_chimeric = models.BooleanField(null=False, blank=False, default=False)
    kDa = models.DecimalField(
        decimal_places=3, max_digits=7, blank=True, null=True)
    preparation = models.CharField(max_length=100, blank=True)
    taxonomy = models.ManyToManyField(FactorTaxonomy)

    @property
    def fullname(self):
        nameList = [tax.fullname for tax in self.taxonomy.all()]
        return f"{'-'.join(nameList)}" if len(nameList) > 1 else nameList[0]

    def __str__(self):
        return self.fullname


class Larvae_stage(models.Model):
    stage = models.CharField(max_length=50)

    def __str__(self):
        return self.stage


class Toxin_distribution(models.Model):
    distribution_choice = models.CharField(max_length=255)

    def __str__(self):
        return self.distribution_choice

class TargetSpeciesStrain(models.Model):
    strain = models.CharField(max_length=50)

    def __str__(self):
        return self.strain

class Target(models.Model):
    target_organism_taxonomy = models.ForeignKey(SpeciesTaxonomy, on_delete=models.CASCADE)
    larvae_stage = models.ForeignKey(Larvae_stage, on_delete=models.CASCADE, blank=True)
    factor_resistance = models.CharField(max_length=255, null=True, blank=True)
    target_species_strain = models.ForeignKey(TargetSpeciesStrain, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.target_organism_taxonomy.name


class Toxin_quantity(models.Model):
    measurement_type = models.CharField(max_length=50, blank=True)
    values = models.CharField(max_length=50)
    units = models.CharField(max_length=50, blank=True, null=True)

    @property
    def quantity(self):
        if self.values == 'reference':
            return self.values
        return f"{self.values} {self.units}" if self.units else f"{self.values} ratio"

    def __str__(self):
        return '{} | {}{}'.format(self.measurement_type, self.values, '' if self.units is None else ' ' + self.units)


class Bioassay_type(models.Model):
    bioassay_type = models.CharField(max_length=20)

    def __str__(self):
        return self.bioassay_type


class Result(models.Model):
    SYNERGISM = 'SYN'
    ANTAGONISM = 'ANT'
    INDEPENDENT = 'IND'
    POSSIBLE_INTERACTIONS = (
        (SYNERGISM, 'Synergism'),
        (ANTAGONISM, 'Antagonism'),
        (INDEPENDENT, 'Additive')
    )
    percentile = models.PositiveIntegerField(blank=True, null=True)
    bioassay_type = models.ForeignKey(Bioassay_type, on_delete=models.CASCADE)
    bioassay_result = models.CharField(max_length=20)
    bioassay_unit = models.CharField(max_length=20, blank=True)
    LC95min = models.CharField(max_length=50, blank=True)
    LC95max = models.CharField(max_length=50, blank=True)
    expected = models.CharField(max_length=20, blank=True)
    interaction = models.CharField(
        max_length=3,
        choices=POSSIBLE_INTERACTIONS,
        blank=True
    )
    synergism_factor = models.CharField(max_length=100, blank=True)
    antagonism_factor = models.CharField(max_length=100, blank=True)
    estimation_method = models.CharField(max_length=100, blank=True)
    slopeLC = models.CharField(max_length=100, blank=True)
    slopeSE = models.CharField(max_length=100, blank=True)
    chi_square = models.CharField(max_length=100, blank=True)


class Toxin_research(models.Model):
    toxin = models.ManyToManyField(Active_factor)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    days_of_observation = models.CharField(max_length=100)
    toxin_distribution = models.ForeignKey(
        Toxin_distribution, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Toxin_quantity, on_delete=models.CASCADE, null=True, blank=True)
    results = models.ForeignKey(Result, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)

    @property
    def factors(self):
        return ' + '.join(toxin.fullname for toxin in self.toxin.all())

    def __str__(self):
        toxins = ', '.join(str(tox) for tox in self.toxin.all())
        return 'Toxin(s): {} | Publication: {} | Target: {} | Bioassay duration: {} | Toxin distribution: {} | Toxin quantity: {} | Results: {}'.format(toxins,
         self.publication.__str__(), self.target.__str__(), self.days_of_observation, self.toxin_distribution.__str__(), self.quantity.__str__(), self.results.__str__())

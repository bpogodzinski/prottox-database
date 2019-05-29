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
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    taxonomy_rank = models.ForeignKey(SpeciesTaxonomyRank, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class FactorTaxonomy(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

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

    def __str__(self):
        return "Name: {} Surname: {}".format(self.name, self.surname)


class Factor_form(models.Model):
    form = models.CharField(max_length=30)

    def __str__(self):
        return self.form


class Publication(models.Model):
    date = models.DateField()
    authors = models.ManyToManyField(Author)
    pubmed_id = models.CharField(max_length=50, blank=True)
    article_link = models.CharField(max_length=200, blank=True)

    def __str__(self):
        all_authors = ", ".join(str(author) for author in self.authors.all())
        return "{} | {}".format(self.date, all_authors)


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
        return f"({' & '.join(nameList)})" if len(nameList) > 1 else nameList[0]

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
    units = models.values = models.CharField(max_length=50, blank=True, null=True)

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
        (INDEPENDENT, 'Independent')
    )
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

    def __str__(self):
        toxins = ', '.join(str(tox) for tox in self.toxin.all())
        return 'Toxin(s): {} | Publication: {} | Target: {} | Days of observation: {} | Toxin distribution: {} | Toxin quantity: {} | Results: {}'.format(toxins,
         self.publication.__str__(), self.target.__str__(), self.days_of_observation, self.toxin_distribution.__str__(), self.quantity.__str__(), self.results.__str__())

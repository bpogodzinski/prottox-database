from django.db import models
from django.db import migrations

class Family_rank_1(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Family_rank_2(models.Model):
    name = models.CharField(max_length=10)
    family_rank_1 = models.ForeignKey(Family_rank_1, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Family_rank_3(models.Model):
    name = models.CharField(max_length=10)
    family_rank_2 = models.ForeignKey(Family_rank_2, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Family_rank_4(models.Model):
    name = models.CharField(max_length=10)
    family_rank_3 = models.ForeignKey(Family_rank_3, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name + self.surname

class Toxin_form(models.Model):
    form = models.CharField(max_length=30)

class Publication(models.Model):
    date = models.DateField()
    authors = models.ManyToManyField(Author)
    pubmed_id = models.CharField(max_length=50, blank=True)
    article_link = models.CharField(max_length=200, blank=True)


class Target_organism_name(models.Model):
    name = models.CharField(max_length=100)

class Toxin_source(models.Model):
    source = models.CharField(max_length=50)

class Toxin_isolation_source(models.Model):
    isolation_source = models.CharField(max_length=40)

class Toxin_expression_host(models.Model):
    host = models.CharField(max_length=40)

class Toxin(models.Model):
    CULTURE = 'C'
    SPORES_CRYSTALS = 'S+C'
    PURIFIED_CRYSTALS = 'PC'
    CELL_LYSATE = 'CL'
    CELL_LYSATE_PARTIAL_PURIFICATION = 'CLPP'
    INCLUSION_BODIES = 'IB'
    INCLUSION_BODIES_SOLUBILIZED = 'IBS'
    PURIFIED_PROTEINS = 'PP'

    POSSIBLE_TOXIN_PREPARATION = (
        (CULTURE,'Culture'),
        (SPORES_CRYSTALS,'Spores + crystals'),
        (PURIFIED_CRYSTALS,'Purified crystals'),
        (CELL_LYSATE,'Cell lysate'),
        (CELL_LYSATE_PARTIAL_PURIFICATION,'Cell lysate with partial purification'),
        (INCLUSION_BODIES,'Inclusion bodies'),
        (INCLUSION_BODIES_SOLUBILIZED,'Inclusion bodies solubilized'),
        (PURIFIED_PROTEINS,'Purified proteins')
    )

    family_rank_4 = models.ForeignKey(Family_rank_4, on_delete=models.CASCADE)
    toxin_source = models.ForeignKey(Toxin_source, on_delete=models.CASCADE)
    NCBI_accession_number = models.CharField(max_length=20, blank=True)
    toxin_form = models.ForeignKey(Toxin_form, on_delete=models.CASCADE)
    isolation_source = models.ForeignKey(Toxin_isolation_source, on_delete=models.CASCADE, blank=True)
    modification_description = models.TextField(blank=True)
    toxin_expression_host = models.ForeignKey(Toxin_expression_host, on_delete=models.CASCADE)
    kDa = models.IntegerField(blank=True, null=True)
    preparation = models.CharField(
        max_length=5,
        choices=POSSIBLE_TOXIN_PREPARATION,
        default=CELL_LYSATE,
        blank=True
    )

    def __str__(self):
        return "{}{}{}{}".format(self.family_rank_1.name, self.family_rank_2.name, self.family_rank_3.name, self.family_rank_4.name)

class Larvae_stage(models.Model):
    stage = models.CharField(max_length=50)

class Toxin_distribution(models.Model):
    SURFACE_CONTAMINATION = 'SC'
    DIET_INCORPORATION = 'DI'
    FORCE_FEEDING = 'FF'
    DROPLET_FEEDING = 'DF'
    POSSIBLE_TOXIN_DISTRIBUTIONS = (
        (SURFACE_CONTAMINATION, 'Surface contamination'),
        (DIET_INCORPORATION, 'Diet incorporation'),
        (FORCE_FEEDING, 'Force feeding'),
        (DROPLET_FEEDING, 'Droplet feeding'),
    )

    distribution_choice = models.CharField(
        max_length=2,
        choices=POSSIBLE_TOXIN_DISTRIBUTIONS,
        default=SURFACE_CONTAMINATION,
    )

class Target(models.Model):
    target_organism_name = models.ForeignKey(Target_organism_name, on_delete=models.CASCADE)
    larvae_stage = models.ForeignKey(Larvae_stage, on_delete=models.CASCADE)
    toxin_resistance = models.ManyToManyField(Toxin, blank=True)

    def __str__(self):
        return self.target_organism_name

class Measurement(models.Model):
    measurement_unit_weight = models.CharField(max_length=5)
    measurement_unit_area = models.CharField(max_length=5)

    def __str__(self):
        return "{}/{}".format(self.measurement_unit_weight, self.measurement_unit_area)

class Toxin_quantity(models.Model):
    BY_WEIGHT = 'BW'
    BY_PROPORTION = 'BP'
    POSSIBLE_MEASUREMENT_TYPE = (
        (BY_WEIGHT, 'Weight'),
        (BY_PROPORTION, 'Proportion')
    )
    measurement_type = models.CharField(
        max_length=2,
        choices=POSSIBLE_MEASUREMENT_TYPE,
        default=BY_PROPORTION
    )
    values = models.CharField(max_length=50)
    units = models.ForeignKey(Measurement, on_delete=models.CASCADE, blank=True, null=True)

class Bioassay_type(models.Model):
    bioassay_type = models.CharField(max_length=20)

class Results(models.Model):
    SYNERGISM = 'SYN'
    ANTAGONISM = 'ANT'
    INDEPENDENT = 'INT'
    POSSIBLE_INTERACTIONS = (
        (SYNERGISM, 'Synergism'),
        (ANTAGONISM, 'Antagonism'),
        (INDEPENDENT, 'Independent')
    )
    bioassay_type = models.ForeignKey(Bioassay_type, on_delete=models.CASCADE)
    bioassay_result = models.CharField(max_length=20)
    bioassay_unit = models.ForeignKey(Measurement, on_delete=models.CASCADE, blank=True)
    LC95min = models.CharField(max_length=50, blank=True)
    LC95max = models.CharField(max_length=50, blank=True)
    expected = models.CharField(max_length=20, blank=True)
    interaction = models.CharField(
        max_length=3,
        choices=POSSIBLE_INTERACTIONS,
        blank=True
    )
    synergism_factor = models.DecimalField(max_digits=7, decimal_places=3, blank=True)
    antagonism_factor = models.DecimalField(max_digits=7, decimal_places=3, blank=True)    

class Toxin_research(models.Model):
    toxin = models.ManyToManyField(Toxin)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    days_of_observation = models.IntegerField()
    toxin_distribution = models.ForeignKey(Toxin_distribution, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Toxin_quantity, on_delete=models.CASCADE)
    results = models.ForeignKey(Results, on_delete=models.CASCADE)
    


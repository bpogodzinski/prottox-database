from django.db import models


class Taxonomy(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


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


class Target_organism_name(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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
    taxonomy = models.ManyToManyField(Taxonomy)


class Larvae_stage(models.Model):
    stage = models.CharField(max_length=50)

    def __str__(self):
        return self.stage


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

    def __str__(self):
        return self.get_distribution_choice_display()


class Target(models.Model):
    target_organism_name = models.ForeignKey(
        Target_organism_name, on_delete=models.CASCADE)
    larvae_stage = models.ForeignKey(
        Larvae_stage, on_delete=models.CASCADE, blank=True)
    factor_resistance = models.ManyToManyField(Active_factor, blank=True)

    def __str__(self):
        resistances = ", ".join(str(factor)
                                for factor in self.factor_resistance.all())
        return "{} | {}{}".format(self.target_organism_name.name, self.larvae_stage.stage, '' if not resistances else ' | ' + resistances)


class Measurement(models.Model):
    measurement_unit_1 = models.CharField(max_length=5)
    measurement_unit_2 = models.CharField(max_length=5)

    def __str__(self):
        return "{}/{}".format(self.measurement_unit_1, self.measurement_unit_2)


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
    units = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '{} | {}{}'.format(self.get_measurement_type_display(), self.values, '' if self.units is None else ' ' + self.units.__str__())


class Bioassay_type(models.Model):
    bioassay_type = models.CharField(max_length=20)

    def __str__(self):
        return self.bioassay_type


class Result(models.Model):
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
    bioassay_unit = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, blank=True, null=True)
    LC95min = models.CharField(max_length=50, blank=True)
    LC95max = models.CharField(max_length=50, blank=True)
    expected = models.CharField(max_length=20, blank=True)
    interaction = models.CharField(
        max_length=3,
        choices=POSSIBLE_INTERACTIONS,
        blank=True
    )
    synergism_factor = models.DecimalField(
        max_digits=7, decimal_places=3, blank=True, null=True)
    antagonism_factor = models.DecimalField(
        max_digits=7, decimal_places=3, blank=True, null=True)

    def __str__(self):
        return '{} {}{} {}{} {} {}'.format(self.bioassay_type.bioassay_type, self.bioassay_result, '%' if self.bioassay_unit is None else ' ' + self.bioassay_unit.__str__(),
                                          '' if not self.LC95max else 'LC95 max: ' + self.LC95max, '' if not self.LC95min else ' LC95 min: ' + self.LC95min, self.get_interaction_display(), self.synergism_factor if self.synergism_factor is not None else self.antagonism_factor)


class Toxin_research(models.Model):
    toxin = models.ManyToManyField(Active_factor)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    days_of_observation = models.IntegerField()
    toxin_distribution = models.ForeignKey(
        Toxin_distribution, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Toxin_quantity, on_delete=models.CASCADE)
    results = models.ForeignKey(Result, on_delete=models.CASCADE)

    def __str__(self):
        toxins = ', '.join(str(tox) for tox in self.toxin.all())
        return 'Toxin(s): {} | Publication: {} | Target: {} | Days of observation: {} | Toxin distribution: {} | Toxin quantity: {} | Results: {}'.format(toxins,
         self.publication.__str__(), self.target.__str__(), self.days_of_observation, self.toxin_distribution.__str__(), self.quantity.__str__(), self.results.__str__())

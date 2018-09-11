from django.db import models
from django.template.defaultfilters import slugify
from django.shortcuts import reverse

from tags.models import Tagable


class Concept(Tagable):
    view_name = ''

    @property
    def slug(self):
        """Return a slug used for anchoring"""
        return slugify(self.short_name)

    @classmethod
    def get_list_url(cls):
        return reverse('animation:{}'.format(cls.view_name))

    def get_list_url_form_instance(self):
        return self.__class__.get_list_url()

    def get_absolute_url(self):
        return reverse('animation:{}'.format(self.__class__.view_name),
                       args=(self.slug,))

    class Meta:
        abstract = True


class Field(Concept):
    name = models.CharField(max_length=20)
    full_name = models.CharField(max_length=50)
    name_fr = 'Axes'
    view_name = 'axes'

    @property
    def long_name(self):
        return self.full_name

    @property
    def short_name(self):
        return self.name

    @property
    def prefere_short(self):
        return True

    def __str__(self):
        return "[Axe] {}".format(self.name)


class Training(Concept):
    name = models.CharField(max_length=50)
    name_fr = 'Formations'
    view_name = 'formations'

    @property
    def long_name(self):
        return self.name

    @property
    def short_name(self):
        return self.name

    @property
    def prefere_short(self):
        return True

    def __str__(self):
        return "[Formation] {}".format(self.name)

    @property
    def slug(self):
        s = super().slug
        if len(s) == 0:
            return "unknown"
        else:
            return s


class Skill(Concept):
    name = models.CharField(max_length=500)
    fields = models.ManyToManyField(Field)
    advices = models.TextField(max_length=1024, blank=True)
    name_fr = 'Compétences'
    view_name = 'competences'

    @property
    def long_name(self):
        return self.name

    @property
    def short_name(self):
        return '{}_{}'.format(self.__class__.view_name, self.id)

    def get_fields(self):
        return self.fields.all()

    def __str__(self):
        return "[Comp. {}] {}".format(self.pk-13, self.name)


class Module(Concept):
    name = models.CharField(max_length=50)
    of_training = models.ForeignKey(Training, on_delete=models.PROTECT)
    skills = models.ManyToManyField(Skill)
    name_fr = 'Modules'
    view_name = 'modules'

    class Meta:
        ordering = 'of_training', 'name'

    @property
    def long_name(self):
        return self.name

    @property
    def short_name(self):
        return self.name

    @property
    def prefere_short(self):
        return True

    def get_skills(self):
        return self.skills.all()

    def __str__(self):
        return "[Module] {}".format(self.name)


class Criterion(Concept):
    name = models.CharField(max_length=500)
    skills = models.ManyToManyField(Skill)
    name_fr = 'Critères'
    view_name = 'criteres'

    class Meta:
        ordering = ('name',)

    @property
    def long_name(self):
        return self.name

    @property
    def short_name(self):
        return '{}_{}'.format(self.__class__.view_name, self.id)

    def get_skills(self):
        return self.skills.all()

    def __str__(self):
        return "[Critère] {}".format(self.name)




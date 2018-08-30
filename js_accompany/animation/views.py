from django.shortcuts import render
from django.http import HttpResponse

from .models import *

from collections import namedtuple


Sticker = namedtuple('Sticker', ['model', 'name', 'components'])

Navigation = namedtuple('Navigation', ['name', 'address', 'focus'])


class MainCategory(object):
    def __init__(self, name, address, list):
        self.name = name
        self.address = address
        self.list = list

    @classmethod
    def get_fields(cls, order_by='id'):
        return Field.objects.order_by(order_by)

    @classmethod
    def get_trainings(cls, order_by='id'):
        return Training.objects.order_by(order_by)

    @classmethod
    def get_modules(cls, order_by='id'):
        return Module.objects.order_by(order_by)

    @classmethod
    def get_skills(cls, order_by='fields'):
        return Skill.objects.order_by(order_by)

    @classmethod
    def get_criteria(cls, order_by='id'):
        return Criterion.objects.order_by(order_by)

    @classmethod
    def from_(cls, Model_cls, sticker_list):
        return MainCategory(Model_cls.name_fr, Model_cls.linkable_name,
                            sticker_list)


class Category(MainCategory):
    def __init__(self, name, address, list, short=False):
        super().__init__(name, address, list)
        self.short = short
        self.is_raw = False

    @classmethod
    def from_iterable(cls, iterable, name, address, short=False):
        components = list(iterable)
        return cls(name=name, address=address, list=components, short=short)

    @classmethod
    def fields(cls, iterable, short=True):
        return cls.from_iterable(iterable, Field.name_fr,
                                 Field.linkable_name, short)

    @classmethod
    def trainings(cls, iterable, short=True):
        return cls.from_iterable(iterable, Training.name_fr,
                                 Training.linkable_name, short)

    @classmethod
    def skills(cls, iterable, short=False):
        return cls.from_iterable(iterable, Skill.name_fr,
                                 Skill.linkable_name, short)

    @classmethod
    def modules(cls, iterable, short=True):
        return cls.from_iterable(iterable, Module.name_fr,
                                 Module.linkable_name, short)

    @classmethod
    def criteria(cls, iterable, short=False):
        return cls.from_iterable(iterable, Criterion.name_fr,
                                 Criterion.linkable_name, short)

    @classmethod
    def fields_from_skills(cls, skills, short=True):
        d = {}
        for skill in skills:
            d.update({x.id: x for x in skill.get_fields()})
        return cls.fields(d.values(), short)

    @classmethod
    def trainings_from_modules(cls, modules, short=True):
        trainings = {m.training for m in modules}
        return cls.trainings(trainings, short)

    @classmethod
    def skills_from_fields(cls, fields, short=False):
        d = {}
        for field in fields:
            d.update({x.id: x for x in
                      Skill.objects.filter(fields=field.id).distinct()})
        return cls.skills(d.values(), short)

    @classmethod
    def skills_from_modules(cls, modules, short=False):
        d = {}
        for module in modules:
            d.update({x.id: x for x in module.get_skills()})
        return cls.skills(d.values(), short)

    @classmethod
    def skills_from_criteria(cls, criteria, short=False):
        d = {}
        for criterion in criteria:
            d.update({x.id: x for x in criterion.get_skills()})
        return cls.skills(d.values(), short)

    @classmethod
    def modules_from_trainings(cls, trainings, short=True):
        d = {}
        for training in trainings:
            d.update({x.id: x for x in
                      Module.objects.filter(training=training.id).distinct()})
        return cls.modules(d.values(), short)

    @classmethod
    def modules_from_skills(cls, skills, short=True):
        skill_ids = [skill.id for skill in skills]
        modules = Module.objects.filter(skills__in=skill_ids).distinct()
        return cls.modules(modules, short)

    @classmethod
    def criteria_from_skills(cls, skills, short=False):
        skill_ids = [skill.id for skill in skills]
        criteria = Criterion.objects.filter(skills__in=skill_ids).distinct()
        return cls.criteria(criteria, short)

    def get_ids(self):
        return [s.id for s in self.list]

    def __iter__(self):
        return iter(self.list)


def create_navigation(model_cls):
    return tuple((
        Navigation(Model.name_fr, Model.linkable_name, Model is model_cls)
        for Model in (Field, Training, Skill, Module, Criterion)
    ))


def fields(request):
    field_stickers = []
    for field in MainCategory.get_fields():
        skill_category = Category.skills_from_fields([field])

        module_category = Category.modules_from_skills(skill_category)

        training_category = Category.trainings_from_modules(module_category)

        criterion_category = Category.criteria_from_skills(skill_category)

        field_stickers.append(Sticker(field, field.long_name,
                                      [training_category, module_category,
                                       skill_category, criterion_category]))

    view = MainCategory.from_(Field, field_stickers)
    return render(request, 'animation/stickers.html/',
                  {'view': view, 'navigation': create_navigation(Field)})


def trainings(request):
    training_stickers = []
    for training in MainCategory.get_trainings():
        module_category = Category.modules_from_trainings([training])

        skill_category = Category.skills_from_modules(module_category)

        criterion_category = Category.criteria_from_skills(skill_category)

        field_category = Category.fields_from_skills(skill_category)

        training_stickers.append(Sticker(training, training.name,
                                         [field_category, module_category,
                                          skill_category, criterion_category]))

    view = MainCategory.from_(Training, training_stickers)
    return render(request, 'animation/stickers.html/',
                  {'view': view, 'navigation': create_navigation(Training)})


def modules(request):
    module_stickers = []
    for module in MainCategory.get_modules():
        training_category = Category.trainings_from_modules([module])

        skill_category = Category.skills_from_modules([module])

        field_category = Category.fields_from_skills(skill_category)

        criterion_category = Category.criteria_from_skills(skill_category)

        module_stickers.append(Sticker(module, module.name,
                                       [training_category, field_category,
                                        skill_category, criterion_category]))

    view = MainCategory.from_(Module, module_stickers)
    return render(request, 'animation/stickers.html/',
                  {'view': view, 'navigation': create_navigation(Module)})


def skills(request):
    skill_stickers = []
    for skill in MainCategory.get_skills():
        field_category = Category.fields_from_skills([skill])

        module_category = Category.modules_from_skills([skill])

        training_category = Category.trainings_from_modules(module_category)

        advice_category = Category("Conseils", "conseil", [skill.advices],
                                   short=False)
        advice_category.is_raw = True

        criterion_category = Category.criteria_from_skills([skill])

        skill_stickers.append(Sticker(skill, skill.name,
                                      [field_category, training_category,
                                       module_category, criterion_category,
                                       advice_category]))

    view = MainCategory.from_(Skill, skill_stickers)
    return render(request, 'animation/stickers.html/',
                  {'view': view, 'navigation': create_navigation(Skill)})


def criteria(request):
    criterion_stickers = []
    for criterion in MainCategory.get_criteria():
        skill_category = Category.skills_from_criteria([criterion])

        field_category = Category.fields_from_skills(skill_category)

        module_category = Category.modules_from_skills(skill_category)

        training_category = Category.trainings_from_modules(module_category)

        criterion_stickers.append(Sticker(criterion, criterion.name,
                                          [field_category, training_category,
                                           module_category, skill_category]))
    view = MainCategory.from_(Criterion, criterion_stickers)
    return render(request, 'animation/stickers.html/',
                  {'view': view, 'navigation': create_navigation(Criterion)})


def unassigned(request):
    Missing = namedtuple('Missing', ['heading', 'id', 'address', 'list'])
    MissingList = namedtuple('MissingList', ['list', 'n_missings'])

    # Skill-based stuff
    exists = set()
    missing_field_from_skills = []
    missing_adives = []
    for skill in Skill.objects.all():
        fields = skill.get_fields()
        # Skill - Field
        if len(fields) == 0:
            missing_field_from_skills.append(skill)
        exists.update({f.id for f in fields})
        # Skill - Advice
        if skill.advices is None or len(skill.advices) == 0:
            missing_adives.append(skill)
    missing_skill_for_field = Field.objects.exclude(id__in=exists)

    # - Skill without field
    missing_field_from_skills = Missing(
        'Compétences sans axe',
        'field_from_skills',
        Skill.linkable_name,
        missing_field_from_skills
    )

    # - Field without skills
    missing_skill_for_field = Missing(
        'Axe vide (aucune compétence)',
        'skill_for_field',
        Field.linkable_name,
        missing_skill_for_field
    )

    # Skill - advices
    missing_advices_from_skills = Missing(
        'Compétences sans conseil',
        'advice_from_skill',
        Skill.linkable_name,
        missing_adives
    )

    # Module - Training
    missing_training_for_modules = Missing(
        'Modules non-assignés (aucune formation)',
        'training_for_module',
        Module.linkable_name,
        Module.objects.filter(training__name="??")
    )

    # Module-based stuff
    exists = set()
    missing_skill_for_module = []
    for module in Module.objects.all():
        skills = module.get_skills()
        if len(skills) == 0:
            missing_skill_for_module.append(module)
        exists.update({s.id for s in skills})
    missing_module_for_skill = Skill.objects.exclude(id__in=exists)

    # - Skill without module
    missing_module_for_skill = Missing(
        'Compétences non-assignées (aucun module)',
        'module_for_skill',
        Skill.linkable_name,
        missing_module_for_skill
    )

    # - module without skill
    missing_skill_for_module = Missing(
        'Modules vides (aucune compétence)',
        'skill_for_module',
        Module.linkable_name,
        missing_skill_for_module
    )

    # Criterion-based stuff
    exists = set()
    missing_skill_for_criterion = []
    for criterion in Criterion.objects.all():
        skills = criterion.get_skills()
        if len(skills) == 0:
            missing_skill_for_criterion.append(criterion)
        exists.update({s.id for s in skills})
    missing_criterion_for_skill = Skill.objects.exclude(id__in=exists)

    # - Skill without criterion
    missing_criterion_for_skill = Missing(
        'Compétences non-évaluées (aucun critère)',
        'criterion_for_skill',
        Skill.linkable_name,
        missing_criterion_for_skill
    )
    # - Criterion without skill
    missing_skill_for_criterion = Missing(
        'Critères inutiles (aucune compétence)',
        'skill_for_criterion',
        Criterion.linkable_name,
        missing_skill_for_criterion
    )

    missings = [
        missing_skill_for_field,
        missing_skill_for_module,
        missing_field_from_skills,
        missing_training_for_modules,
        missing_module_for_skill,
        missing_criterion_for_skill,
        missing_skill_for_criterion,
        missing_advices_from_skills
    ]

    missing_list = MissingList(missings, sum(len(m.list) for m in missings))
    return render(request, 'animation/unassigned.html/',
                  {'missings': missing_list,
                   'display_empty': True})

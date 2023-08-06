import sys
import inspect
import copy
from ..lib.customer import find_usecase
from django.apps import AppConfig

class EnrichAppConfig(AppConfig):

    name="default"
    category = "default"
    verbose_name = "default"
    description = "default"
    filename = None
    enable = False
    multiple = False
    composition = False
    entry = "index"
    tags = ["store"]
    _readme = ""

    @property
    def readme(cls):
        if hasattr(cls, 'get_readme'):
            return cls.get_readme()
        elif cls._readme == "":
            return cls.description
        else:
            return cls._readme

    def get_usecase(self):

        if self.filename is None:
            return {}

        usecase = find_usecase(self.filename)
        self.usecase = copy.deepcopy(usecase)
        return self.usecase

    def is_composition(self):
        return self.composition

    def get_name(self):
        return self.name

    def get_verbose_name(self):
        return self.verbose_name

    def get_description(self):
        return self.description

    def is_enabled(self):
        return self.enable

    def __str__(self):
        return f"{self.name}: {self.verbose_name}"



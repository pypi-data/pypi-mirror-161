from __future__ import annotations

import logging
import typing as T
import yaml

from itertools import starmap
from django.core.management.commands.runserver import Command as BaseCommand

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from labeltree.models import Label
from labeltree.models import LabelGroup



class Command(BaseCommand):
    help = "Update label groups in the database based on the given YAML file."

    def add_arguments(self, parser):
        parser.add_argument('file_name')

    def handle(self, file_name, **kwargs):

        groups, species = SpeciesGroup.read(file_name)

        for group in groups:
            name = group.name
            species = Label.objects.filter(name__in=group.species)

            if len(species) != len(group.species):
                import pdb; pdb.set_trace()
            assert len(species) == len(group.species)

            parent = set([spec.parent for spec in species])

            assert len(parent) == 1

            parent = list(parent)[0]

            obj, created = LabelGroup.objects.get_or_create(name=name)

            obj.parent = parent
            obj.species.set(species)
            obj.save()


class SpeciesGroup(T.NamedTuple):
    name: str
    species: T.List[str]

    @classmethod
    def read(cls, file_name):
        group_list = []
        group_list_reverse = {}
        if file_name is not None:
            with open(file_name, "r") as f:
                group_list = cls.new(yaml.load(f, Loader))

            group_list_reverse = {species: group
                for group in group_list
                    for species in group.species
            }

        return group_list, group_list_reverse


    @staticmethod
    def check(name0, name1, sep=" / "):
        first0, *rest0 = name0.split(sep)
        first1, *rest1 = name1.split(sep)

        genus0, *first_spec0 = first0.split()
        genus1, *first_spec1 = first1.split()

        specs0 = set(first_spec0 + rest0)
        specs1 = set(first_spec1 + rest1)

        return genus0 == genus1 and (specs1.issubset(specs0) or specs0.issubset(specs1))


    @classmethod
    def new(cls, species_groups: T.Dict[str, T.List[str]]) -> T.List[SpeciesGroup]:
        return list(starmap(SpeciesGroup, species_groups.items()))
        # same as following:
        # return [
        #     SpeciesGroup(group_name, species) for group_name, species in species_groups.items()
        # ]


    def __eq__(self, group_or_name):

        if isinstance(group_or_name, SpeciesGroup):
            group_or_name = group_or_name.name

        if not isinstance(group_or_name, str):
            raise TypeError(f"Unsupported type: {type(group_or_name).__name__}")

        return SpeciesGroup.check(self.name, group_or_name)


    def __contains__(self, name):
        return name in self.species

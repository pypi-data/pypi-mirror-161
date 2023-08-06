from __future__ import annotations

import logging
import numpy as np
import requests
import typing as T


from collections import OrderedDict
from django.core.management.commands.runserver import Command as BaseCommand
from tqdm.auto import tqdm
from urllib.parse import quote
from urllib.parse import urlencode

from labeltree.management.commands.addgroups import SpeciesGroup
from labeltree.models import Label

def _nansafe(value):
    return None if value is np.nan else value


class Command(BaseCommand):
    help = "Update labels in the database based on the given CSV file."

    def add_arguments(self, parser):
        parser.add_argument('file_name')

        parser.add_argument('--sep', default=";")

        parser.add_argument('--taxon_ranks',
            nargs="*", default=("order", "family", "genus"))

        parser.add_argument("--order")
        parser.add_argument("--skip_by_name", action="store_true")

        parser.add_argument("--species_group_file",
            help="Path to a file containing species groupings")

    def handle(self, *args,
        file_name,
        sep: str,
        taxon_ranks: T.Tuple[str] = (Label.Rank.ORDER, Label.Rank.FAMILY, Label.Rank.GENUS),
        order: T.Optional[str] = None,
        skip_by_name: bool = False,
        species_group_file: str = None,
        **kwargs):


        content = np.loadtxt(file_name,
            dtype=[("name", "U255"), ("kr_nr", "U255")],
            delimiter=sep)

        group_list, _ = SpeciesGroup.read(species_group_file)

        entries = OrderedDict()
        db_entries = set(Label.objects.values_list("id", flat=True))
        db_names = set(Label.objects.values_list("name", flat=True))

        for i, entry in enumerate(tqdm(content)):
            name, kr_nr = entry["name"], entry["kr_nr"]

            if skip_by_name and name in db_names:
                continue

            if name in group_list:
                # species groups are handled in another command
                continue
                import pdb; pdb.set_trace()


            matched = GBIFEntry.match(name,
                kr_nr=kr_nr,
                order=order, ranks=taxon_ranks,
                already_matched=db_entries | entries.keys())

            for entry in matched:
                entries[entry.key] = entry
                try:
                    _new_label(entry)
                except Exception as e:
                    import pdb; pdb.set_trace()
                    raise



        labels = []
        for key, entry in entries.items():
            label, created = _new_label(entry, save=False)
            if created:
                labels.append(label)

        Label.objects.bulk_create(labels, batch_size=1000)

class GBIFEntry(T.NamedTuple):
    canonicalName: str
    rank: str
    authorship: str

    key: int
    parentKey: int

    kr_nr: T.Optional[str] = None

    URL = "https://api.gbif.org/v1/"

    @classmethod
    def _get(cls, path: str, query: T.Optional = None) -> T.Dict:

        url = f"{cls.URL}{path}"

        if query is not None:
            query_str = urlencode(query, quote_via=quote)
            url = f"{url}?{query_str}"

        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @classmethod
    def new(cls, fields: dict) -> GBIFEntry:
        return cls(**{key: fields.get(key, None) for key in cls._fields})

    @classmethod
    def match(cls,
              name: str,
              kr_nr: T.Optional[str] = "",
              order: T.Optional[str] = None,
              ranks: T.Tuple[str] = (),
              already_matched: T.Set = set()) -> T.List[GBIFEntry]:

        result = []

        def _add_result(key, extra_fields={}):

            while True:
                if key in already_matched:
                    return

                fields = cls._get(f"species/{key}")

                if fields["rank"].lower() in Label.Rank:
                    break

                assert key != fields["parentKey"], \
                    f"Key was also set as parentKey: {key}"

                key = fields["parentKey"]

            entry = cls.new(fields | extra_fields)
            result.append(entry)

        query = dict(name=name)
        if order:
            query["order"] = order

        match = cls._get("species/match", query)

        assert match["matchType"] in ["EXACT", "FUZZY"], \
            f"Failed to match {name} ({match})!"

        synonymKey = None
        matchedKey = match["usageKey"]

        if match["synonym"]:
            synonymKey = matchedKey
            matchedKey = match["acceptedUsageKey"]

        matchedRank = match["rank"].lower()

        for rank in ranks:
            if rank == matchedRank:
                break

            _add_result(match[f"{rank}Key"])

        _add_result(matchedKey, dict(kr_nr=kr_nr))

        if synonymKey is not None:
            _add_result(synonymKey, dict(kr_nr=kr_nr))

        return result



def _new_label(entry: GBIFEntry, save: bool = True) -> Label:

    parent = entry.parentKey if entry.rank.lower() != Label.Rank.ORDER else None
    created = False
    try:
        label = Label.objects.get(
            id=entry.key,
            name=entry.canonicalName,
            taxonomic_rank=entry.rank.lower())


        assert label.parent_id == parent, \
            f"Data mismatch {label.parent=} != {parent=}"

        assert label.kr_nr and label.kr_nr == entry.kr_nr, \
            f"Data mismatch {label.kr_nr=} != {entry.kr_nr=}"
        assert label.authors == entry.authorship, \
            f"Data mismatch {label.authors=} != {entry.authorship=}"

    except Label.DoesNotExist:
        label = Label(
            id=entry.key,
            name=entry.canonicalName,
            taxonomic_rank=entry.rank.lower(),
            parent_id = parent,
            kr_nr = entry.kr_nr,
            authors = entry.authorship,
        )
        created = True


    if save:
        label.save()

    return label, created


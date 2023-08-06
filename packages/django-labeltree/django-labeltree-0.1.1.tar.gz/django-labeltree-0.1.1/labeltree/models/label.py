import enum
import re

from django.core import validators
from django.db import models

from rest_framework import serializers

from labeltree.models import base

class Label(base.BaseModel):

    class Language(models.TextChoices):
        GERMAN = "de"
        ENGLISH = "en"
        UNDEFINED = "undefined"

    class Rank(models.TextChoices):
        ORDER = "order"
        FAMILY = "family"
        GENUS = "genus"
        SPECIES = "species"

    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"

        unique_together = [
            ("name", "taxonomic_rank"),
            ("name", "kr_nr")
        ]

    def __str__(self):
        if self.kr_nr:
            return f"{self.name} {self.kr_nr} [{self.taxonomic_rank}]"

        return f"{self.name} [{self.taxonomic_rank}]"

    serializer_fields = base.BaseModel.serializer_fields + (
        "name", "taxonomic_rank", "parent_id",
        "kr_nr", "phonetic_name", "phonetic_name_language",
    )
    read_only_fields = base.BaseModel.read_only_fields + (
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Scentific name",
    )

    taxonomic_rank = models.CharField(
        max_length=255,
        verbose_name="Taxonomic Rank",
        choices=Rank.choices,
        default=Rank.SPECIES,
    )

    parent = models.ForeignKey(
        to="self",
        verbose_name="Parent",
        related_name="children",
        related_query_name="child",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    kr_nr = models.CharField(
        max_length=255,
        verbose_name="K+R-Nr.",
        validators=[validators.RegexValidator(
            regex=re.compile(r"[A-Za-z0-9]+"),
            message="K+R numbers should be alpha-numeric only!"
        )],
        blank=True,
        null=True,
    )

    phonetic_name = models.CharField(
        max_length=255,
        verbose_name="Phonetic name",
        blank=True,
        null=True
    )

    phonetic_name_language = models.CharField(
        max_length=255,
        verbose_name="Phonetic lanugage",
        choices=Language.choices,
        default=Language.UNDEFINED,
    )

    authors = models.CharField(
        max_length=255,
        verbose_name="Authors",
        blank=True,
        null=True
    )




class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = Label.serializer_fields
        read_only_fields = Label.read_only_fields

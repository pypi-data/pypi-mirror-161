from django.db import models

from rest_framework import serializers

from labeltree.models import base
from labeltree.models import label

class LabelGroup(base.BaseModel):

    class Meta:
        verbose_name = "Label Group"
        verbose_name_plural = "Label Groups"

    def __str__(self):
        return super().__str__()

    serializer_fields = base.BaseModel.serializer_fields + (
        "name",
        "parent_id",
        "species",
    )

    read_only_fields = base.BaseModel.read_only_fields + (
        "species",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Group name",
    )

    parent = models.ForeignKey(label.Label,
        on_delete=models.SET_NULL,
        verbose_name="Parent",
        related_name="child_groups",
        blank=True, null=True,
        limit_choices_to=dict(taxonomic_rank=label.Label.Rank.GENUS),
    )

    species = models.ManyToManyField(label.Label,
        related_name="group",
        limit_choices_to=dict(taxonomic_rank=label.Label.Rank.SPECIES)
    )

class LabelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = LabelGroup
        fields = LabelGroup.serializer_fields
        read_only_fields = LabelGroup.read_only_fields

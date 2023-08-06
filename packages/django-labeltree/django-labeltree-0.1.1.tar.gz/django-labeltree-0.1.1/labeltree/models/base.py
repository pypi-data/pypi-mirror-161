
from django.db import models


class BaseModel(models.Model):

    class Meta:
        abstract = True


    serializer_fields = (
        "id",
        "created", "last_update"
    )
    read_only_fields = (
        "created", "last_update"
    )

    ############################
    ##### Auto-Date Fields #####
    ############################

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created at",
    )

    last_update = models.DateTimeField(
        auto_now=True,
        verbose_name="Last modified at",
    )


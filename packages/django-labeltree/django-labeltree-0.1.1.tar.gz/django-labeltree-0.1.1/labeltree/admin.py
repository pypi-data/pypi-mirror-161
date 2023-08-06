from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from labeltree.models import Label
from labeltree.models import LabelGroup



@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent_name",
        "children",
        "gbif_link",
        "kr_nr",
        "group_name",

        # "phonetic_name",
        # "phonetic_name_language",

        "authors",
    )


    list_filter = (
        'taxonomic_rank',
        ("group", admin.EmptyFieldListFilter),
        "created",
        "last_update",
    )

    ordering = ['kr_nr', "name"]
    search_fields = ['name', "kr_nr", "parent__name", "phonetic_name"]

    # def has_group(self, obj):
    #     return not obj.group.empty()

    @admin.display(empty_value='-')
    def group_name(self, obj):
        if not obj.group.exists():
            return
        group = obj.group.get()

        url = reverse('admin:labeltree_label_changelist')
        query = f"group__in={group.id}"
        return format_html(f"<a href='{url}?{query}'>{group.name}</a>")

    @admin.display(empty_value='-', ordering="id")
    def gbif_link(self, obj):
        url = f"https://api.gbif.org/v1/species/{obj.id}"
        name = f"{obj.taxonomic_rank.capitalize()} {obj.id}"
        return format_html(f"<a target='_new' href='{url}'>{name}</a>")

    @admin.display(empty_value='-', ordering="parent__name")
    def parent_name(self, obj):
        if obj.parent is None:
            return

        url = reverse('admin:labeltree_label_changelist')
        query = f"parent_id__exact={obj.parent_id}"
        name = obj.parent.name
        return format_html(f"<a href='{url}?{query}'>{name}</a>")

    @admin.display(empty_value='-')
    def children(self, obj):
        count = obj.children.count()
        if count == 0:
            return

        url = reverse('admin:labeltree_label_changelist')
        query = f"parent_id__exact={obj.id}"
        return format_html(f"<a href='{url}?{query}'>{count}</a>")


@admin.register(LabelGroup)
class LabelGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent_name",
        "children"
    )
    ordering = ["name"]
    search_fields = ['name', "parent__name", "species__name"]

    list_filter = ("created", "last_update")


    @admin.display(empty_value='-', ordering="parent__name")
    def parent_name(self, obj):
        if obj.parent is None:
            return

        url = reverse('admin:labeltree_labelgroup_changelist')
        query = f"parent_id__exact={obj.parent_id}"
        name = obj.parent.name
        return format_html(f"<a href='{url}?{query}'>{name}</a>")

    @admin.display(empty_value='-')
    def children(self, obj):
        if obj.species.count() == 0:
            return

        url = reverse('admin:labeltree_label_changelist')
        query = f"group__in={obj.id}"
        name = ", ".join([spec.name for spec in obj.species.all()])
        return format_html(f"<a href='{url}?{query}'>{name}</a>")

from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import routers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from labeltree import models

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = models.LabelSerializer

    def get_queryset(self):
        return models.Label.objects.all()

    pagination_class = StandardResultsSetPagination

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['taxonomic_rank', "parent_id"]
    search_fields = ["name", "kr_nr", "parent__name", "group__name", "phonetic_name"]

class LabelGroupViewSet(viewsets.ModelViewSet):
    serializer_class = models.LabelGroupSerializer

    def get_queryset(self):
        return models.LabelGroup.objects.all()

    pagination_class = StandardResultsSetPagination

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["parent_id"]
    search_fields = ["name", "parent__name", "species__name"]

router = routers.DefaultRouter()
router.register(r"label", LabelViewSet, "label")
router.register(r"label-group", LabelGroupViewSet, "label-group")

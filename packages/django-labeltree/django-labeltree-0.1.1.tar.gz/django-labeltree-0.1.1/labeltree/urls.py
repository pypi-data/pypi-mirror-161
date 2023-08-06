from django.urls import path
from django.urls import include

from labeltree import views

urlpatterns = [
    path('', include(views.router.urls)),
]

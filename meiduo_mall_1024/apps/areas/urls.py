from django.contrib import admin
from django.urls import path

from apps.areas.views import AreaView,SubAreaView

urlpatterns = [
    path('areas/',AreaView.as_view()),
    path('areas/<city_id>/',SubAreaView.as_view()),
]


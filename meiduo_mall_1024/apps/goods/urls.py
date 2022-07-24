from django.contrib import admin
from django.urls import path

from apps.goods.views import IndexView,ListView,HotSellView
from apps.goods.views import SKUSearchView,DetailView

urlpatterns = [
    path('index/',IndexView.as_view()),
    path('list/<category_id>/skus/',ListView.as_view()),
    path('hot/<category_id>/',HotSellView.as_view()),
    path('search/',SKUSearchView()),
    path('detail/<sku_id>/', DetailView.as_view()),
]


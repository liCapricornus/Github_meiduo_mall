from django.contrib import admin
from django.urls import path

from apps.oauth.views import QQLoginURLView,OAuthQQView

urlpatterns = [
    path('qq/authorization/',QQLoginURLView.as_view()),
    path('oauth_callback/',OAuthQQView.as_view()),
]


from django.contrib import admin
from django.urls import path
from apps.users.views import RegisterView,UsernameCountView,MobileCountView

urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view()),  # /mobiles/' + this.mobile + '/count/
    path('register/',RegisterView.as_view()),
]


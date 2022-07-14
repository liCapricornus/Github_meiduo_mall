from django.contrib import admin
from django.urls import path
from apps.users.views import RegisterView,UsernameCountView,MobileCountView
from apps.users.views import LoginView,LogoutView,CenterView

urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view()),  # /mobiles/' + this.mobile + '/count/
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('center/',CenterView.as_view()),
]


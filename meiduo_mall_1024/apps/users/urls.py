from django.contrib import admin
from django.urls import path
from apps.users.views import RegisterView,UsernameCountView,MobileCountView
from apps.users.views import LoginView,LogoutView,CenterView
from apps.users.views import EmailView,EmailVerifyView,AddressCreateView
from apps.users.views import AddressView,AddressOperationView,AddressDefaultView
from apps.users.views import AddressUpdateTitle,UpdateUserPassword
from apps.users.views import UserHistoryView

urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view()),  # /mobiles/' + this.mobile + '/count/
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('info/',CenterView.as_view()),
    path('emails/',EmailView.as_view()),
    path('emails/verification/',EmailVerifyView.as_view()),
    path('addresses/create/', AddressCreateView.as_view()),
    path('addresses/', AddressView.as_view()),
    path('addresses/<address_id>/', AddressOperationView.as_view()),
    path('addresses/<address_id>/default/', AddressDefaultView.as_view()),
    path('addresses/<address_id>/title/', AddressUpdateTitle.as_view()),
    path('password/', UpdateUserPassword.as_view()),
    path('browse_histories/', UserHistoryView.as_view()),
]


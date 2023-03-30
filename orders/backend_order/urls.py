from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *
from django.urls import path

urlpatterns = [
    path('shoplist/', SendShopList.as_view()),
    path('login/', UserLogin.as_view()),
    path('register/', UserRegister.as_view()),
    path('contact/', AddUserAddressView.as_view()),
    path('basket/', BasketView.as_view()),
    path('confirm/', OrderConfirmationView.as_view()),
    path('thanks/', ThankForOrderView.as_view())
]

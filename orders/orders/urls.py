"""orders URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from backend_order.views import *

r = DefaultRouter()
r.register('products', ProductViewSet)
r.register('product_detail', ProductInShopViewSet)
r.register('orders/<int:pk>/', OrderViewSet)
r.register('orders', OrderViewSet)
r.register('order_detail', OrderItemViewSet)
r.register('order_detail/<int:pk>/', OrderItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', obtain_auth_token),
    path('accounts/', include('allauth.urls')),
    path('api/', include('backend_order.urls')),
    path('api/', include(r.urls)),
]

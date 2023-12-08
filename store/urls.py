from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
     path('', views.home, name='home'),
     path('shop/', views.shop, name='shop'),

]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.lobby),
    path('room/', views.room),
    path('login/', views.login),

]
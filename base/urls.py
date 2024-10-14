from django.urls import path
from . import views

urlpatterns = [
    path('', views.lobby),
    path('room/', views.room),
    path('login/', views.login),
    path('get_token/', views.getToken),
    path('create_member/',views.createMember)
]
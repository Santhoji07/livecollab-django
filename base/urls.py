from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('', views.lobby, name='lobby'),
    path('room/', views.room, name='room'),
    path('get_token/', views.getToken),
    path('create_member/',views.createMember),
    path('get_member/',views.getMember),
    path('delete_member/',views.deleteMember),
]
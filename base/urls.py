from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('lobby', views.lobby, name='lobby'),
    path('room/', views.room, name='room'),
    path('get_token/', views.getToken),
    path('create_member/',views.createMember),
    path('get_member/',views.getMember),
    path('delete_member/',views.deleteMember),
]
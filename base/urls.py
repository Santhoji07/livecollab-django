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
    path('join_room/<str:room_name>/', views.handle_join_request),
    path('check_pending_requests/<str:room_name>/', views.check_pending_requests),
    path('approve_join_request/<str:room_name>/<int:request_id>/', views.approve_join_request),
    path('check_join_request_status/<str:room_name>/<int:user_id>/', views.check_join_request_status),
    path('get_participants/<str:room_name>/', views.get_participants),
    path('get_uid_by_username/', views.getUidByUsername),
    path('remove_participant_by_name/', views.remove_participant_by_name),
    path('change_host/', views.change_host, name='change_host'),
]
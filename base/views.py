from django.shortcuts import render, redirect
from django.http import JsonResponse
from agora_token_builder import RtcTokenBuilder
import random
import time
import json
from .models import RoomMember
from django.views.decorators.csrf import csrf_exempt

from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

@login_required(login_url='/login/')  # Optional: Require login for homepage
def home(request):
    return render(request, 'base/home.html') 

# View to handle user login with a custom template and redirection for authenticated users.
class CustomLoginView(LoginView):
     # Specify the template to be used for the login page
    template_name = 'base/login.html'
    # Allow all fields to be included in the form (note: this is usually not recommended for security reasons)
    fields = '__all__'
    # Redirect authenticated users to another page instead of showing the login page
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirect to the 'lobby' URL upon successful login
        return reverse_lazy('lobby')
     

# View to handle user sign-up, including account creation and automatic login upon successful registration.
class SignUp(FormView):
    # Specify the template to be used for the sign-up page
    template_name = 'base/signup.html'
    # Use the UserCreationForm for signing up new users
    form_class = UserCreationForm
    # Redirect authenticated users to another page instead of showing the sign-up page
    redirect_authenticated_user = True
    # Specify the URL to redirect to upon successful form submission
    success_url = reverse_lazy('lobby')

    def form_valid(self, form):
        # Save the user and log them in if the form is valid
        user = form.save()
        if user is not None:
            login(self.request, user)  # Log in the newly created user
        return super(SignUp, self).form_valid(form)  # Proceed with the usual form validation flow
    
    def get(self, *args, **kwargs):
        # Check if the user is already authenticated
        if self.request.user.is_authenticated:
            # Redirect authenticated users to the 'lobby'
            return redirect('lobby')
        
        return super(SignUp, self).get(*args, **kwargs)  # Otherwise, render the sign-up page


# Ensure that the user is logged in before accessing the decorated view
@login_required(login_url='/login/')
# View to generate an Agora RTC token.
def getToken(request):
    # Agora app credentials (replace with actual credentials for production use).
    appId = '351d9881f5d3413ba18e08949844fddb'
    appCertificate = '8061ce92be7f4e8caea5650c67ddc7ce'
    
    # Get the channel name from the request.
    channelName = request.GET.get('channel')
    
    # Generate a random UID (User ID) between 1 and 230.
    uid = random.randint(1, 230)
    
    # Set the token expiration time to 24 hours (3600 seconds * 24).
    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = time.time()  # Get current timestamp.
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds  # Set the privilege expiration timestamp.
    
    role = 1  # Define the role (1 means broadcaster).
    
    # Build the Agora RTC token using the UID and other details.
    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    
    # Return the generated token and UID as a JSON response.
    return JsonResponse({'token': token, 'uid': uid}, safe=False)


# Ensure that the user is logged in before accessing the decorated view
@login_required(login_url='/login/')
# View to render the lobby page.
def lobby(request):
    return render(request, 'base/lobby.html')


# Ensure that the user is logged in before accessing the decorated view
@login_required(login_url='/login/')
# View to render the room page.
def room(request):
    return render(request, 'base/room.html')


# Ensure that the user is logged in before accessing the decorated view
@login_required(login_url='/login/')
# View to create a new RoomMember entry in the database.
@csrf_exempt  # Exempt from CSRF protection since the request method is POST and coming from JavaScript.
def createMember(request):
    data = json.loads(request.body)  # Load JSON data from the request body.
    
    # Get or create a new RoomMember entry based on the user's name, UID, and room name.
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],  # Member's name.
        uid=data['UID'],    # User's unique identifier (UID).
        room_name=data['room_name']  # Room name.
    )

    # Return the user's name in a JSON response.
    return JsonResponse({'name': data['name']}, safe=False)


# Ensure that the user is logged in before accessing the decorated view
@login_required(login_url='/login/')
# View to fetch a RoomMember's information based on UID and room name.
def getMember(request):
    uid = request.GET.get('UID')  # Get the UID from the query parameters.
    room_name = request.GET.get('room_name')  # Get the room name from the query parameters.

    # Find the RoomMember entry that matches the UID and room name.
    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )

    # Return the member's name as a JSON response.
    return JsonResponse({'name': member.name}, safe=False)


# Ensure that the user is logged in before accessing the decorated view
@login_required(login_url='/login/')
# View to delete a RoomMember entry from the database.
@csrf_exempt  # Exempt from CSRF protection since this is a DELETE request from JavaScript.
def deleteMember(request):
    data = json.loads(request.body)  # Load JSON data from the request body.
    
    # Find the RoomMember entry based on the user's name, UID, and room name.
    member = RoomMember.objects.get(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name'],
    )

    # Delete the RoomMember entry.
    member.delete()
    
    # Return a confirmation message as a JSON response.
    return JsonResponse('Member was deleted', safe=False)

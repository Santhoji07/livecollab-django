from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from agora_token_builder import RtcTokenBuilder
import random
import time
import json
from .models import RoomMember, Room, RoomRequest

from django.views.decorators.csrf import csrf_exempt

from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def home(request):
    return render(request, 'base/home.html') 

def about(request):
    return render(request, 'base/about.html')

def contact(request):
    return render(request, 'base/contact.html')

# View to handle user login with a custom template and redirection for authenticated users.
class CustomLoginView(LoginView):
     # Specify the template to be used for the login page
    template_name = 'base/login.html'
    # Allow all fields to be included in the form (note: this is usually not recommended for security reasons)
    fields = '__all__'
    # Redirect authenticated users to another page instead of showing the login page
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirect to the 'home' URL upon successful login
        return reverse_lazy('home')
     

# View to handle user sign-up, including account creation and automatic login upon successful registration.
class SignUp(FormView):
    # Specify the template to be used for the sign-up page
    template_name = 'base/signup.html'
    # Use the UserCreationForm for signing up new users
    form_class = UserCreationForm
    # Redirect authenticated users to another page instead of showing the sign-up page
    redirect_authenticated_user = True
    # Specify the URL to redirect to upon successful form submission
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Save the user and log them in if the form is valid
        user = form.save()
        if user is not None:
            login(self.request, user)  # Log in the newly created user
        return super(SignUp, self).form_valid(form)  # Proceed with the usual form validation flow
    
    def get(self, *args, **kwargs):
        # Check if the user is already authenticated
        if self.request.user.is_authenticated:
            # Redirect authenticated users to the 'home'
            return redirect('home')
        
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

    # Get action type (host/join)
    action_type = request.GET.get('actionType')

    # Check if the room already exists only if the user is hosting
    if action_type == 'host':
        # Query the database to check if a room with the given channel name already exists.
        existing_room = Room.objects.filter(room_name=channelName).first()
        # If the room already exists, return an error response.
        if existing_room:
            return JsonResponse({'error': 'Room already exists'}, status=400)

    # Check if the room exists when the user is trying to join.   
    elif action_type == 'join':
        # Query the database to check if a room exists
        existing_room = Room.objects.filter(room_name=channelName).first()
        # If the room does not exist, return an error response.
        if not existing_room:
            return JsonResponse({'error': 'Room does not exist'}, status=404)
        
    # Generate a random UID (User ID) between 1 and 230.
    uid = random.randint(1, 230)
    
    # Set the token expiration time to 24 hours (3600 seconds * 24).
    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = time.time()  # Get current timestamp.
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds  # Set the privilege expiration timestamp.
    
    role = 1  # Define the role (1 means broadcaster).
    
    # Build the Agora RTC token using the UID and other details.
    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

    # If the user is hosting, create a new Room entry in the database.
    if action_type == 'host':
        # Create the room object
        room = Room.objects.create(room_name=channelName, current_host=request.user, token=token, uid=uid)

        # Add the host as the first participant
        room.participants.add(request.user)
    
    # Return the generated token and UID as a JSON response.
    return JsonResponse({'token': token, 'uid': uid}, safe=False)


# Ensure that the user is logged in before accessing the decorated view
@login_required(login_url='/login/')
# View to render the lobby page.
def lobby(request):
    action_type = request.GET.get('actionType', 'join')  # Default to 'join' if not specified
    return render(request, 'base/lobby.html', {'action_type': action_type})


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
    
    try:
        # Find the RoomMember entry based on the user's name, UID, and room name
        member = RoomMember.objects.get(
            name=data['name'],
            uid=data['UID'],
            room_name=data['room_name'],
        )

        # Delete the RoomMember entry
        member.delete()
        
        # Find the Room entry for the specified room
        room = Room.objects.get(room_name=data['room_name'])
        
        # Remove the user from the participants list
        room.participants.remove(request.user)

        # Check if there are any members remaining in the room
        remaining_members = RoomMember.objects.filter(room_name=data['room_name']).exists()

        # If the leaving member is the host, set the current_host field to null
        if room.current_host == request.user:
            room.current_host = None
            room.save()

        # If no members remain in the room, delete the Room entry
        if not remaining_members:
            room.delete()

        # Return a confirmation message as a JSON response
        return JsonResponse('Member was deleted', safe=False)

    except RoomMember.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)


# Endpoint for handling join requests
def handle_join_request(request, room_name):
    # Ensure the request method is POST
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
    # Get the room object
    room = get_object_or_404(Room, room_name=room_name)
    user = request.user
    
    # Check if the room has a host
    if room.current_host:
        # Check if there is an existing pending request for this user in the room
        room_request, created = RoomRequest.objects.get_or_create(
            room=room,
            user=user,
            defaults={'status': 'pending'}
        )
        
        if not created and room_request.status == 'pending':
            # If a request is already pending, return the existing pending status
            return JsonResponse({"status": "pending_approval", "message": "Already waiting for host approval"}, status=403)
        
        # Set the request status to 'pending' and save it
        room_request.status = 'pending'
        room_request.save()
        
        # Notify the host here 
        return JsonResponse({"status": "pending_approval", "message": "Waiting for host approval"}, status=403)
    
    # If no host exists, allow the user to join automatically without any RoomRequest
    room.participants.add(user)
    return JsonResponse({"status": "approved", "message": "User approved to join the room"})


def check_pending_requests(request, room_name):
    try:
        # Retrieve the room by name
        room = Room.objects.get(room_name=room_name)
        
        # Check if the requesting user is the host
        is_host = request.user == room.current_host

        # Get the pending requests for this room
        pending_requests = RoomRequest.objects.filter(room=room, status='pending')
        
        # Serialize the data
        requests_data = [{"name": req.user.username, "user_id": req.id} for req in pending_requests]

        return JsonResponse({"status": "success", "pending_requests": requests_data, "is_host": is_host})
    
    except Room.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Room not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


def approve_join_request(request, room_name, request_id):
    try:
        # Fetch the room and request
        room = get_object_or_404(Room, room_name=room_name)  # Get room based on room_name
        join_request = get_object_or_404(RoomRequest, id=request_id, room=room)

        # Parse the JSON body to get the 'approve' flag
        data = json.loads(request.body)
        approve = data.get("approve", False)

        if approve:
            # Approve the request
            join_request.status = 'approved'
            join_request.save()
            # Add the user to the room participants
            room.participants.add(join_request.user)
            message = "Request approved, user added to room."
        else:
            # Deny the request
            join_request.status = 'denied'
            join_request.save()
            message = "Request denied."

        # Return a response indicating success
        return JsonResponse({
            "status": "success",
            "message": message
        })

    except Room.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Room not found"})
    except RoomRequest.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Join request not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


def check_join_request_status(request, room_name, user_id):
    try:
        # Fetch the room and request
        room = get_object_or_404(Room, room_name=room_name)  # Get room based on room_name
        join_request = get_object_or_404(RoomRequest, user_id=user_id, room=room)

        # Check the status of the join request
        if join_request.status == 'approved':
            # If the request is approved, indicate the user can proceed to the room
            return JsonResponse({
                "status": "success",
                "join_status": "approved",
                "redirect_url": "/room/",  # Include the redirect URL here
                "message": "Your request to join has been approved!"
            })

        elif join_request.status == 'denied':
            # If the request is denied, inform the user
            return JsonResponse({
                "status": "success",
                "join_status": "denied",
                "message": "Your request to join was denied."
            })

        else:
            # If the request is still pending
            return JsonResponse({
                "status": "success",
                "join_status": "pending",
                "message": "Your request is still pending."
            })
    
    except RoomRequest.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Join request not found."
        }, status=404)


# View to get the list of participants in a room
@login_required(login_url='/login/')
def get_participants(request, room_name):
    try:
        # Fetch the room by name
        room = Room.objects.get(room_name=room_name)

        # Get all participants in the room
        participants = room.participants.all()

        # Serialize participant usernames
        participants_data = [{"username": participant.username} for participant in participants]

        return JsonResponse({"status": "success", "participants": participants_data})

    except Room.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Room not found"}, status=404)
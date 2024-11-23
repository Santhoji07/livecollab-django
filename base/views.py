from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from agora_token_builder import RtcTokenBuilder
import random
import time
import json
from .models import RoomMember, Room, RoomRequest, User

from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


# View for the homepage (render the 'home.html' template).
def home(request):
    return render(request, 'base/home.html') 


# View for the About Us page (render the 'about.html' template).
def about(request):
    return render(request, 'base/about.html')


# View for the Contact Us page (render the 'contact.html' template).
def contact(request):
    return render(request, 'base/contact.html')


# Custom view for handling user login.
# Uses a custom template and redirects authenticated users away from the login page.
class CustomLoginView(LoginView):
    template_name = 'base/login.html'  # Specify the custom login page template
    fields = '__all__'  # Allows all fields in the form (usually not recommended for security).
    redirect_authenticated_user = True  # If the user is already logged in, redirect them to home.

    # If login is successful, redirect to the 'home' page.
    def get_success_url(self):
        return reverse_lazy('home')


# View for handling user sign-up, including account creation and automatic login.
class SignUp(FormView):
    template_name = 'base/signup.html'  # Specify the template for the sign-up page.
    form_class = UserCreationForm  # Use the built-in Django UserCreationForm for new users.
    redirect_authenticated_user = True  # Redirect authenticated users to the home page.
    success_url = reverse_lazy('home')  # Redirect to home after successful sign-up.

    # Custom behavior when the form is successfully validated:
    def form_valid(self, form):
        user = form.save()  # Save the new user.
        if user is not None:
            login(self.request, user)  # Log the user in immediately after signing up.
        return super(SignUp, self).form_valid(form)  # Proceed with usual form handling.
    
    # Check if the user is already authenticated. If so, redirect to the home page.
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')  # Redirect to home if the user is already logged in.
        return super(SignUp, self).get(*args, **kwargs)  # Otherwise, render the sign-up page.


# View to generate an Agora RTC token for room participation or creation.
# This view is only accessible to authenticated users.
@login_required(login_url='/login/')    # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def getToken(request):
    # Agora app credentials (these are placeholder values, should be replaced with actual ones).
    appId = '351d9881f5d3413ba18e08949844fddb'
    appCertificate = '8061ce92be7f4e8caea5650c67ddc7ce'
    
    # Get the channel name (room) and action type (host/join) from the request.
    channelName = request.GET.get('channel')
    action_type = request.GET.get('actionType')

    # If the user is hosting, check if a room with the given channel name already exists.
    if action_type == 'host':
        existing_room = Room.objects.filter(room_name=channelName).first()
        if existing_room:
            return JsonResponse({'error': 'Room already exists'}, status=400)  # Return error if the room exists.

    # If the user is joining, ensure the room exists.
    elif action_type == 'join':
        existing_room = Room.objects.filter(room_name=channelName).first()
        if not existing_room:
            return JsonResponse({'error': 'Room does not exist'}, status=404)  # Return error if the room does not exist.
    
    # Generate a random UID between 1 and 230 (to simulate user identity in Agora).
    uid = random.randint(1, 230)
    
    # Set the expiration time of the token to 24 hours.
    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = time.time()
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds  # Calculate the expiration timestamp.
    
    role = 1  # Assign a role of 1 for the broadcaster (host).

    # Build the Agora RTC token using the credentials, UID, and channel information.
    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

    # If the user is hosting, create a new room entry in the database.
    if action_type == 'host':
        room = Room.objects.create(room_name=channelName, current_host=request.user, token=token, uid=uid)
        room.participants.add(request.user)  # Add the host as the first participant in the room.
    
    # Return the generated token and UID as a JSON response.
    return JsonResponse({'token': token, 'uid': uid}, safe=False)


# View to render the lobby page, accessible only by logged-in users.
@login_required(login_url='/login/')    # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def lobby(request):
    action_type = request.GET.get('actionType', 'join')  # Default action is 'join' if not specified.
    return render(request, 'base/lobby.html', {'action_type': action_type})


# View to render the room page, accessible only by logged-in users.
@login_required(login_url='/login/') # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def room(request):
    return render(request, 'base/room.html')


# View to create a new RoomMember entry in the database.
@login_required(login_url='/login/') # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def createMember(request):
    data = json.loads(request.body)  # Parse the JSON data from the request body.
    
    # Create or get a RoomMember entry based on the user's name, UID, and room name.
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )

    # Return the member's name as a JSON response.
    return JsonResponse({'name': data['name']}, safe=False)


# View to fetch a RoomMember's information based on UID and room name.
@login_required(login_url='/login/')    # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def getMember(request):
    uid = request.GET.get('UID')  # Get UID from request query parameters.
    room_name = request.GET.get('room_name')  # Get room name from request query parameters.

    # Find the member from the database using the provided UID and room name.
    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )

    # Return the member's name as a JSON response.
    return JsonResponse({'name': member.name}, safe=False)


# View to delete a RoomMember entry from the database.
@login_required(login_url='/login/')    # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def deleteMember(request):
    data = json.loads(request.body)  # Parse the request body as JSON.
    try:
        # Find the RoomMember entry based on the user's name, UID, and room name.
        member = RoomMember.objects.get(
            name=data['name'],
            uid=data['UID'],
            room_name=data['room_name'],
        )

        # Delete the RoomMember entry.
        member.delete()

        # Find the Room entry associated with the specified room name.
        room = Room.objects.get(room_name=data['room_name'])
        
        # Remove the user from the participants list of the room.
        room.participants.remove(request.user)

        # If the leaving member was the host, set the room's host to None.
        if room.current_host == request.user:
            room.current_host = None
            room.save()

        # If no members remain in the room, delete the room entry from the database.
        if not RoomMember.objects.filter(room_name=data['room_name']).exists():
            room.delete()

        # Return a confirmation message as a JSON response.
        return JsonResponse('Member was deleted', safe=False)

    except RoomMember.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)  # Return error if the member is not found.
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)  # Return error if the room is not found.


# Endpoint for handling join requests
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def handle_join_request(request, room_name):    
    # Get the room object based on the room_name provided in the URL
    room = get_object_or_404(Room, room_name=room_name)
    user = request.user
    
    # Check if the room has a host
    if room.current_host:
        # Check if there is an existing pending request for this user to join the room
        room_request, created = RoomRequest.objects.get_or_create(
            room=room,
            user=user,
            defaults={'status': 'pending'}
        )
        
        # If there is already a pending request, inform the user that they're waiting for approval
        if not created and room_request.status == 'pending':
            return JsonResponse({"status": "pending_approval", "message": "Already waiting for host approval"}, status=403)
        
        # Otherwise, set the request status to 'pending' and save the request
        room_request.status = 'pending'
        room_request.save()
        
        # Inform the user that they are waiting for host approval
        return JsonResponse({"status": "pending_approval", "message": "Waiting for host approval"}, status=403)
    
    # If no host exists, automatically approve the user to join the room
    room.participants.add(user)
    return JsonResponse({"status": "approved", "message": "User approved to join the room"})


# Endpoint to check all pending join requests for a room
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def check_pending_requests(request, room_name):
    try:
        # Retrieve the room based on its name
        room = Room.objects.get(room_name=room_name)
        
        # Check if the requesting user is the host
        is_host = request.user == room.current_host

        # Get all pending requests for the room
        pending_requests = RoomRequest.objects.filter(room=room, status='pending')
        
        # Prepare the data for the pending requests
        requests_data = [{"name": req.user.username, "user_id": req.id} for req in pending_requests]

        # Return the list of pending requests along with whether the user is the host
        return JsonResponse({"status": "success", "pending_requests": requests_data, "is_host": is_host})
    
    except Room.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Room not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


# Endpoint for the host to approve or deny a join request
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def approve_join_request(request, room_name, request_id):
    try:
        # Fetch the room and the join request based on the room_name and request_id
        room = get_object_or_404(Room, room_name=room_name)
        join_request = get_object_or_404(RoomRequest, id=request_id, room=room)

        # Parse the JSON body to check if the request should be approved or denied
        data = json.loads(request.body)
        approve = data.get("approve", False)

        if approve:
            # If approved, change the status of the request and add the user to the room
            join_request.status = 'approved'
            join_request.save()
            room.participants.add(join_request.user)
            message = "Request approved, user added to room."
        else:
            # If denied, change the request status to 'denied'
            join_request.status = 'denied'
            join_request.save()
            message = "Request denied."

        # Return a success message indicating the decision
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


# Endpoint to check the status of a user's join request
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def check_join_request_status(request, room_name, user_id):
    try:
        # Fetch the room and the join request for the user
        room = get_object_or_404(Room, room_name=room_name)
        join_request = get_object_or_404(RoomRequest, user_id=user_id, room=room)

        # Check the current status of the join request and return an appropriate response
        if join_request.status == 'approved':
            # If approved, provide the user with the ability to proceed to the room
            return JsonResponse({
                "status": "success",
                "join_status": "approved",
                "redirect_url": "/room/",  # Provide a link to the room
                "message": "Your request to join has been approved!"
            })

        elif join_request.status == 'denied':
            # If denied, inform the user that their request was rejected
            return JsonResponse({
                "status": "success",
                "join_status": "denied",
                "message": "Your request to join was denied."
            })

        else:
            # If still pending, inform the user that their request is waiting for approval
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
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def get_participants(request, room_name):
    try:
        # Fetch the room by its name
        room = Room.objects.get(room_name=room_name)

        # Get all participants of the room
        participants = room.participants.all()

        # Prepare the data for all participants with "is_host" field
        participants_data = [
            {
                "username": participant.username,
                "is_host": participant == room.current_host  # Check if the participant is the current host
            }
            for participant in participants
        ]

        # Return the list of participants
        return JsonResponse({"status": "success", "participants": participants_data})

    except Room.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Room not found"}, status=404)


# View to fetch a RoomMember's UID based on username and room name.
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def getUidByUsername(request):
    # Retrieve the username and room name from the request's query parameters.
    username = request.GET.get('username')
    room_name = request.GET.get('room_name')

    try:
        # Query the RoomMember model to find the member with the specified username and room name.
        member = RoomMember.objects.get(
            name=username,
            room_name=room_name,
        )

        # If found, return the member's UID in a JSON response.
        return JsonResponse({'uid': member.uid}, safe=False)

    except RoomMember.DoesNotExist:
        # If no matching member is found, return a 404 error with an appropriate message.
        return JsonResponse({'error': 'Member not found'}, status=404)


# View to remove a participant from a room using their name and room_name.
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def remove_participant_by_name(request):
    # Parse the JSON request body to extract the participant's data.
    data = json.loads(request.body)
    
    try:
        # Query the RoomMember model to find the participant to be removed using their name, UID, and room name.
        member = RoomMember.objects.get(
            name=data['name'],
            uid=data['UID'],
            room_name=data['room_name'],
        )

        # Remove the member from the RoomMember model.
        member.delete()

        # Query the Room model to find the corresponding room using the room name.
        room = Room.objects.get(room_name=data['room_name'])

        # Find the participant to remove from the room's participants list by matching their username (case-insensitively).
        participant_to_remove = room.participants.filter(username__iexact=member.name).first()

        # If the participant exists in the room, remove them.
        if participant_to_remove:
            room.participants.remove(participant_to_remove)

        # If the removed participant was the current host, set the room's host to None.
        if room.current_host == participant_to_remove:
            room.current_host = None
            room.save()

        # If the room no longer has any participants, delete the room from the database.
        if not room.participants.exists():
            room.delete()

        # Return a success response indicating the participant was removed successfully.
        return JsonResponse({'message': f'Participant {member.name} has been removed successfully.'}, safe=False)

    except RoomMember.DoesNotExist:
        # Return a 404 error if the specified member does not exist.
        return JsonResponse({'error': 'Member not found.'}, status=404)

    except Room.DoesNotExist:
        # Return a 404 error if the specified room does not exist.
        return JsonResponse({'error': 'Room not found.'}, status=404)

    except Exception as e:
        # Catch any unexpected errors and return a 500 response with the error message.
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


# View to change the host of a room.
@login_required(login_url='/login/')  # Ensure the user is logged in before accessing this view. Redirects to '/login/' if the user is not logged in
def change_host(request):
    # Parse the JSON request body to extract the new host's data
    data = json.loads(request.body)

    try:
        # Query the Room model to find the room using the room name
        room = Room.objects.get(room_name=data['room_name'])

        # Query the User model to find the new host by username (case-insensitively)
        new_host = User.objects.filter(username__iexact=data['name']).first()

        if not new_host:
            # Return a 404 error if the specified user does not exist
            return JsonResponse({'error': 'User not found.'}, status=404)

        if new_host not in room.participants.all():
            # Return a 400 error if the specified user is not a participant of the room
            return JsonResponse({'error': 'User is not a participant of the room.'}, status=400)

        # Update the room's current host to the new host
        room.current_host = new_host
        room.save()

        # Return a success response indicating the host was changed successfully
        return JsonResponse({'message': f'{new_host.username} is now the host of the room.'}, safe=False)

    except Room.DoesNotExist:
        # Return a 404 error if the specified room does not exist
        return JsonResponse({'error': 'Room not found.'}, status=404)

    except Exception as e:
        # Catch any unexpected errors and return a 500 response with the error message
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

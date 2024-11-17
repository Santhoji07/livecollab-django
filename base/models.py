from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class RoomMember(models.Model):
    name = models.CharField(max_length=200)  # Field to store the member's name.
    uid = models.CharField(max_length=200)    # Field to store a unique identifier for the member (User ID).
    room_name = models.CharField(max_length=200)  # Field to store the name of the room the member belongs to.

    def __str__(self):
        return self.name  # Returns the member's name when the object is printed or represented. 


class Room(models.Model):
    room_name = models.CharField(max_length=255, unique=True, null=True)   # Field to store the unique name of the room.
    current_host = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="hosted_rooms", null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="rooms", blank=True)
    token = models.CharField(max_length=255, null=True)                    # Field to store the generated token for the room.
    uid = models.IntegerField(null=True)                                 # Field to store the user ID associated with the room.
    created_at = models.DateTimeField(auto_now_add=True)        # Automatically records the timestamp when the room token is created.

    def __str__(self):
        return self.room_name  # Returns the room name when the object is printed or represented.
    

class RoomRequest(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)  # Link to the Room model
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who is making the request
    status = models.CharField(max_length=20, default='pending')  # status can be 'pending', 'approved', 'denied'
    created_at = models.DateTimeField(auto_now_add=True)  # Track when the request was made

    def __str__(self):
        return f"Request from {self.user.username} for room {self.room.room_name} ({self.status})"  # Returns the username, room name and status when the object is printed or represented.
    
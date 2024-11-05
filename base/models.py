from django.db import models

# Create your models here.
class RoomMember(models.Model):
    name = models.CharField(max_length=200)  # Field to store the member's name.
    uid = models.CharField(max_length=200)    # Field to store a unique identifier for the member (User ID).
    room_name = models.CharField(max_length=200)  # Field to store the name of the room the member belongs to.

    def __str__(self):
        return self.name  # Returns the member's name when the object is printed or represented.
    
    
class RoomToken(models.Model):
    room_name = models.CharField(max_length=255, unique=True)  # Field to store the unique name of the room.
    token = models.CharField(max_length=255)                    # Field to store the generated token for the room.
    uid = models.IntegerField()                                  # Field to store the user ID associated with the room.
    created_at = models.DateTimeField(auto_now_add=True)        # Automatically records the timestamp when the room token is created.

    def __str__(self):
        return self.room_name  # Returns the room name when the object is printed or represented.

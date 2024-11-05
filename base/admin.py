from django.contrib import admin
from .models import RoomMember, RoomToken

# Register your models here.
admin.site.register(RoomMember)
admin.site.register(RoomToken)
from django.shortcuts import get_object_or_404

from .models import RoomQuery, Room
from main.utils import OwnerPermMixin


class RoomOwnerPermMixin(OwnerPermMixin):
    def get_owner(self, kwargs):
        return get_object_or_404(Room, pk=kwargs["room_id"]).owner


class RoomQueryOwnerPermMixin(OwnerPermMixin):
    def get_owner(self, kwargs):
        return get_object_or_404(RoomQuery, pk=kwargs["query_id"]).sender

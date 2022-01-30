from django.urls import path
from .views import *

urlpatterns = [
    path('room_list/', RoomList.as_view(mode='Действие'), name="room_list"),
    path('my_room_list/', MyRoomList.as_view(mode='Владелец'), name="my_room_list"),

    path('room/new', AddRoom.as_view(), name="add_room"),
    path('room/<int:room_id>/edit/', EditRoom.as_view(), name="edit_room"),
    path('room/<int:room_id>/delete/', DeleteRoom.as_view(), name="delete_room"),
    path('room/<int:room_id>/', ShowRoom.as_view(), name='room'),
    path('room/<int:room_id>/booking_list/', RoomBookingList.as_view(), name="room_booking_list"),
    path('room/<int:room_id>/add_room_query/', AddRoomQuery.as_view(), name='add_room_query'),
    path('room/<int:room_id>/schedule/', RoomSchedule.as_view(), name='room_schedule'),

    path('my_room_booking_list/', MyRoomBookingList.as_view(), name='my_room_booking_list'),
    path('room_query_list/', RoomQueryList.as_view(), name='room_query_list'),
    path('my_room_query_list/', MyRoomQueryList.as_view(), name='my_room_query_list'),
    path('room_query/<int:query_id>/edit/', EditRoomQuery.as_view(), name='edit_room_query'),
    path('room_query/<int:query_id>/delete/', DeleteRoomQuery.as_view(), name='delete_room_query'),
    path('room_query/<int:query_id>/respond/', RespondRoomQuery.as_view(), name='room_query_respond'),
]
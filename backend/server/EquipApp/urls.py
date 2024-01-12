from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('equip_list/', EquipList.as_view(mode='Действие'), name="equip_list"),
    path('my_equip_list/', MyEquipList.as_view(mode='Владелец'), name="my_equip_list"),

    path('equip/new', AddEquip.as_view(), name="add_equip"),
    path('equip/<int:equip_id>/edit/', EditEquip.as_view(), name="edit_equip"),
    path('equip/<int:equip_id>/delete/', DeleteEquip.as_view(), name="delete_equip"),
    path('equip/<int:equip_id>/', ShowEquip.as_view(), name='equip'),
    path('equip/<int:equip_id>/booking_list/', EquipBookingList.as_view(), name="equip_booking_list"),
    path('equip/<int:equip_id>/add_equip_query/', AddEquipQuery.as_view(), name='add_equip_query'),
    path('equip/<int:equip_id>/schedule/', EquipSchedule.as_view(), name='equip_schedule'),

    path('my_equip_booking_list/', MyEquipBookingList.as_view(), name='my_equip_booking_list'),
    path('equip_query_list/', EquipQueryList.as_view(), name='equip_query_list'),
    path('my_equip_query_list/', MyEquipQueryList.as_view(), name='my_equip_query_list'),
    path('equip_query/<int:query_id>/edit/', EditEquipQuery.as_view(), name='edit_equip_query'),
    path('equip_query/<int:query_id>/delete/', DeleteEquipQuery.as_view(), name='delete_equip_query'),
    path('equip_query/<int:query_id>/respond/', RespondEquipQuery.as_view(), name='equip_query_respond'),
    path('equip_search/', EquipSearch.as_view(), name='equip_search')
]

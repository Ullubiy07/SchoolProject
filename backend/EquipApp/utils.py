from django.shortcuts import get_object_or_404

from .models import EquipQuery, Equipment
from main.utils import OwnerPermMixin

class EquipOwnerPermMixin(OwnerPermMixin):
    def get_owner(self, kwargs):
        return get_object_or_404(Equipment, pk=kwargs["equip_id"]).owner

class EquipQueryOwnerPermMixin(OwnerPermMixin):
    def get_owner(self, kwargs):
        return get_object_or_404(EquipQuery, pk=kwargs["query_id"]).sender
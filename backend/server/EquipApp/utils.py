from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from server.main.models import SupplyManager
from .models import EquipQuery, Equipment
from server.main.utils import OwnerPermMixin


class EquipOwnerPermMixin(OwnerPermMixin):
    def get_owner(self, kwargs):
        return get_object_or_404(Equipment, pk=kwargs["equip_id"]).owner


    def dispatch(self, request, *args, **kwargs):
        owner = self.get_owner(kwargs)
        if not request.user.has_perm(SupplyManager.Permission):
            return HttpResponseForbidden("<h1>Страница не доступна</h1>")
        elif request.user.has_perm(SupplyManager.Permission) and owner != request.user.supplymanager.school:
            return HttpResponseForbidden("<h1>Страница не доступна</h1>")
        return super().dispatch(request, *args, **kwargs)


class EquipQueryOwnerPermMixin(OwnerPermMixin):
    def get_owner(self, kwargs):
        return get_object_or_404(EquipQuery, pk=kwargs["query_id"]).sender

    def dispatch(self, request, *args, **kwargs):
        owner = self.get_owner(kwargs)
        if not request.user.has_perm(SupplyManager.Permission):
            return HttpResponseForbidden("<h1>Страница не доступна</h1>")
        elif request.user.has_perm(SupplyManager.Permission) and owner != request.user.supplymanager.school:
            return HttpResponseForbidden("<h1>Страница не доступна</h1>")
        return super().dispatch(request, *args, **kwargs)

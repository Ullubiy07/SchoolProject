from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseForbidden

from .models import Lecture
from main.models import Teacher
from main.utils import OwnerPermMixin

class OwnerPermMixin:
    def dispatch(self, request, *args, **kwargs):
        owner = self.get_owner(kwargs)
        if not request.user.has_perm(Teacher.Permission):
            return HttpResponseForbidden("<h1>Страница не доступна<h1>")
        elif owner != request.user.teacher:
            return HttpResponseForbidden("<h1>Страница не доступна<h1>")
        return super().dispatch(request, *args, **kwargs)

    def get_owner(self, kwargs):
        return None

class LectureOwnerPermMixin(OwnerPermMixin):
    def get_owner(self, kwargs):
        return get_object_or_404(Lecture, pk=kwargs["lecture_id"]).organizer

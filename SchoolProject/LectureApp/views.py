from django.urls.base import reverse_lazy
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin 
from django.contrib import messages

from .models import *
from main.models import *
from main.utils import DataMixin

class LectureList(LoginRequiredMixin, DataMixin, ListView):
    model = Lecture
    template_name = 'LectureApp/lecture_list.html'
    context_object_name = 'lecture_list'
    login_url = reverse_lazy('login')
    mode = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.has_perm(Teacher.Permission):
            context["mode"] = "Просмотр"
        else:
            context["mode"] = self.mode
        c_def = self.get_user_context(title='Список лекций')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        user = self.request.user
        if user.has_perm(Teacher.Permission):
            return Lecture.objects.exclude(organizer=user.teacher)
        else:
            return Lecture.objects.all()

class MyLectureList(PermissionRequiredMixin, LectureList):
    permission_required = Teacher.Permission

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['link'] = reverse('lecture_list')
        context['link_text'] = "Посмотреть общий список лекций"
        context['title_text'] = "Список моих лекций"
        if not context["lecture_list"]:
            context['title_text'] = "У вас нет лекций..."
        return context

    def get_queryset(self):
        return Lecture.objects.filter(organizer=self.request.user.teacher)

class ShowLecture(LoginRequiredMixin, DataMixin, DetailView):
    model = Lecture
    template_name = "LectureApp/lecture_details.html"
    pk_url_kwarg = "lecture_id"
    context_object_name = "lecture"
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
       
        lecture = context["lecture"]
        user = self.request.user
        if not user.has_perm(SchRep.Permission):
            context["mode"] = "Просмотр"
        elif user.teacher == lecture.organizer:
            context["mode"] = "Владелец"
        else:
            context['mode'] = "Действие"
        
        c_def = self.get_user_context(title=lecture.name)
        return dict(list(context.items()) + list(c_def.items()))

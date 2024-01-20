from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import LectureForm
from .models import *
from .utils import *

from main.models import *
from main.utils import DataMixin
from django.db.models import Q


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
            context['perm'] = True
        c_def = self.get_user_context(title='Список лекций')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        user = self.request.user
        if user.has_perm(Teacher.Permission):
            return Lecture.objects.all()    #exclude(organizer=user.teacher)
        else:
            return Lecture.objects.all()


class LectureSearch(ListView, DataMixin):

    template_name = 'LectureApp/lecture_list.html'
    context_object_name = 'lecture_list'

    def get_queryset(self):
        search_query = self.request.GET.get('q', None)
        if search_query:
            result = Lecture.objects.filter(Q(name__icontains=search_query)
                                            |
                                            Q(description__icontains=search_query)
                                            |
                                            Q(category__name__icontains=search_query)
                                            |
                                            Q(address__icontains=search_query)
                                            |
                                            Q(target_audience__name__icontains=search_query))
            if not result.exists():
                result = messages.add_message(self.request, messages.WARNING, 'Лекция не найдена')

        else:
            result = messages.add_message(self.request, messages.WARNING, 'Вы ничего не ввели!')
        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get('q')
        c_def = self.get_user_context()
        return dict(list(context.items()) + list(c_def.items()))



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
        if user.has_perm(Teacher.Permission) and user.teacher == lecture.organizer:
            context["mode"] = "Владелец"
        else:
            context['mode'] = "Действие"

        c_def = self.get_user_context(title=lecture.name)
        return dict(list(context.items()) + list(c_def.items()))


class EditLecture(LectureOwnerPermMixin, DataMixin, UpdateView):
    model = Lecture
    form_class = LectureForm
    pk_url_kwarg = "lecture_id"
    template_name = 'main/form.html'

    def dispatch(self, request, *args, **kwargs):
        lecture = get_object_or_404(Lecture, pk=kwargs["lecture_id"])
        self.initial["lecture"] = lecture
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Изменить параметры лекции"
        context["button_text"] = "Сохранить"
        c_def = self.get_user_context(title='Изменить лекцию')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили параметры лекции.')
        return super().form_valid(form)


class DeleteLecture(LectureOwnerPermMixin, DataMixin, DeleteView):
    model = Lecture
    template_name = 'main/form.html'
    pk_url_kwarg = "lecture_id"
    success_url = reverse_lazy('my_lecture_list')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Удалить лекцию"
        context["button_text"] = "Да"
        context["text"] = "Вы точно хотите удалить лекцию?"
        c_def = self.get_user_context(title='Удалить лекцию')
        return dict(list(context.items()) + list(c_def.items()))

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, 'Вы успешно удалили лекцию.')
        return super().post(request, *args, **kwargs)


class AddLecture(PermissionRequiredMixin, DataMixin, CreateView):
    permission_required = Teacher.Permission
    form_class = LectureForm
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Добавить лeкцию"
        context["button_text"] = "Добавить"
        c_def = self.get_user_context(title='Добавить лекцию')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.organizer = self.request.user.teacher
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно добавили лекцию.')
        return super().form_valid(form)


@login_required(login_url="login")
def create_lecture_record(request, *args, **kwargs):
    lecture = get_object_or_404(Lecture, pk=kwargs["lecture_id"])
    record = LectureRecord.objects.filter(lecture=lecture, user=request.user)
    if (
        request.user.has_perm(Teacher.Permission) or
        request.user.has_perm(SchRep.Permission) or
        request.user.has_perm(SupplyManager.Permission)
    ):
        messages.add_message(request, messages.INFO, 'Вы не можете записаться на лекцию.')
    elif record.exists():
        messages.add_message(request, messages.WARNING, 'Вы уже записались на лекцию.')
    elif lecture.max_places <= lecture.get_record_quantity():
        messages.add_message(request, messages.INFO, 'Все места на лекции заняты')
    else:
        LectureRecord.objects.create(lecture=lecture, user=request.user)
        messages.add_message(request, messages.SUCCESS, 'Вы успешно записались на лекцию')
    return redirect("lecture", lecture_id=lecture.pk)

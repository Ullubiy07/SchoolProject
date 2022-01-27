import os
import schedule
import time
from threading import Thread
from django.contrib.auth import logout, login
from django.http import FileResponse
from django.urls.base import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.conf import settings
import random
from django.contrib.auth.models import Group

from .forms import *
from .models import *
from EquipApp.models import *
from .utils import *


class MyThread(Thread):
    def __init__(self, function, args: dict = None):
        Thread.__init__(self)
        self.function = function
        if args is None:
            args = {}
        self.args = args

    def run(self):
        """Запуск параллельного потока"""
        self.function(**self.args)

def time_manager():
    schedule.every().day.at("14:21").do(clean_db)
    while True:
        schedule.run_pending()
        time.sleep(1)

def clean_db():
    EquipBooking.objects.filter(booking_end__lt=datetime.datetime.today()).delete()
    EquipQuery.objects.filter(booking_end__lt=datetime.datetime.today()).delete()

# Не запускать при разработке и тестах. Только во время работы на сервере.
# TimeManager = MyThread(time_manager)
# TimeManager.start()

class Home(DataMixin, TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        return dict(list(context.items()) + list(c_def.items()))

def generate_random_string(length):
    symbols = "0123456789ABCDABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy"
    gen_str = "".join([symbols[random.randint(0, len(symbols) - 1)] for i in range(length)])
    return gen_str

class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        context["title_text"] = "Регистрация"
        context["button_text"] = "Зарегистрироваться"
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно создали аккаунт')
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Вход')
        context["title_text"] = "Вход"
        context["button_text"] = "Войти"
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

class ChangeUserData(LoginRequiredMixin, DataMixin, UpdateView):
    model = User
    form_class = ChangeUserDataForm
    pk_url_kwarg = "user_id"
    template_name = 'main/form.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('login')

    def get_object(self):
        return self.request.user

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Изменить персональную информацию"
        context["button_text"] = "Сохранить"
        c_def = self.get_user_context(title='Изменить персональную информацию')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили данные аккаунта.')
        return super().form_valid(form)

class ChangePassword(LoginRequiredMixin, DataMixin, PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = 'main/form.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Смена пароля')
        context["title_text"] = "Сменя пароля"
        context["button_text"] = "Изменить пароль"
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

def create_sch_rep_user(request):
    if request.user.has_perm(SchRep.Permission):
        username, password = generate_random_string(8), generate_random_string(8)
        while User.objects.filter(username=username).exists():
            username, password = generate_random_string(8), generate_random_string(8)
        user = User.objects.create_user(username=username, password=password)
        SchRep.objects.create(user=user, school=request.user.schrep.school)
        group = Group.objects.get(name=SchRep.Group)
        user.groups.add(group)
        messages.add_message(request, messages.SUCCESS, f'Вы успешно создали аккаунт школьного представителя. Логин: {username}, Пароль: {password}.'
                                                          ' Сохраните эту информацию перед закрытием сообщения')
        return redirect('home')
    else:
        return HttpResponseForbidden('Доступ запрещен')

def create_teacher(request):
    if request.user.has_perm(SchRep.Permission):
        username, password = generate_random_string(8), generate_random_string(8)
        while User.objects.filter(username=username).exists():
            username, password = generate_random_string(8), generate_random_string(8)
        user = User.objects.create_user(username=username, password=password)
        Teacher.objects.create(user=user, school=request.user.schrep.school)
        group = Group.objects.get(name=Teacher.Group)
        user.groups.add(group)
        messages.add_message(request, messages.SUCCESS, f'Вы успешно создали аккаунт учителя. Логин: {username}, Пароль: {password}.'
                                                          ' Сохраните эту информацию перед закрытием сообщения')
        return redirect('home')
    else:
        return HttpResponseForbidden('Доступ запрещен')

def logout_user(request):
    logout(request)
    return redirect('login')

def install_file(request, file_path):
    return FileResponse(open(os.path.join(settings.MEDIA_ROOT, file_path),'rb'))
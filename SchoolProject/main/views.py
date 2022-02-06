import os
import schedule
import time
from threading import Thread
from django.contrib.auth import logout, login
from django.http import FileResponse
from django.urls.base import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.conf import settings
import random
from django.contrib.auth.models import Group
import aspose.words as aw

from .forms import *
from .models import *
from EquipApp.models import *
from RoomApp.models import *
from LectureApp.models import *
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
    schedule.every().day.at("03:00").do(clean_db)
    while True:
        schedule.run_pending()
        time.sleep(600)

def clean_db():
    EquipBooking.objects.filter(booking_end__lt=datetime.datetime.today() - datetime.timedelta(days=14)).delete()
    EquipQuery.objects.filter(booking_end__lt=datetime.datetime.today()).delete()
    RoomBooking.objects.filter(booking_end__lt=datetime.datetime.today() - datetime.timedelta(days=14)).delete()
    RoomQuery.objects.filter(booking_end__lt=datetime.datetime.today()).delete()
    Lecture.objects.filter(start_datetime__lt=(datetime.datetime.today() - datetime.timedelta(days=1))).delete()

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

class ChangeSchRepSign(PermissionRequiredMixin, DataMixin, UpdateView):
    permission_required = SchRep.Permission
    form_class = SchRepSignForm
    template_name = 'main/form.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Изменить вашу подпись')
        context["title_text"] = "Изменить вашу подпись"
        context["button_text"] = "Изменить"
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили свою подпись.')
        return super().form_valid(form)
    
    def get_object(self):
        return self.request.user.schrep

class ChangeSchoolData(PermissionRequiredMixin, DataMixin, UpdateView):
    permission_required = SchRep.Permission
    form_class = SchoolForm
    template_name = 'main/form.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Изменить данные школы')
        context["title_text"] = "Изменить данные школы"
        context["button_text"] = "Изменить"
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили данные школы.')
        return super().form_valid(form)
    
    def get_object(self):
        return self.request.user.schrep.school

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
    try:
        return FileResponse(open(file_path,'rb'))
    except:
        messages.add_message(request, messages.ERROR, 'Не удается найти файл.')
        return redirect('home')

def create_sign(sign, sign_image, password, sign_line, path):
    try:
        signOptions = aw.digitalsignatures.SignOptions()
            
        signOptions.signature_line_id = sign_line.id
        with open(sign_image.path, "rb") as image_file:
            signOptions.signature_line_image = image_file.read()
            
        certHolder = aw.digitalsignatures.CertificateHolder.create(sign.path, password)
            
        aw.digitalsignatures.DigitalSignatureUtil.sign(path, path, certHolder, signOptions)
        return True
    except:
        return False


def sign_contract(contract_path, sch_rep_1, sch_rep_2):
    try:
        # Получаем строки подписей
        doc = aw.Document(contract_path)
        signatureLine1 = doc.first_section.body.get_child(aw.NodeType.SHAPE, 0, True).as_shape().signature_line
        signatureLine2 = doc.first_section.body.get_child(aw.NodeType.SHAPE, 1, True).as_shape().signature_line
        signatureLine3 = doc.first_section.body.get_child(aw.NodeType.SHAPE, 2, True).as_shape().signature_line
        signatureLine4 = doc.first_section.body.get_child(aw.NodeType.SHAPE, 3, True).as_shape().signature_line
        doc.save(contract_path)

        # Подписываем
        result = create_sign(sch_rep_1.sign, sch_rep_1.sign_image, sch_rep_1.sign_password, signatureLine1, contract_path)
        result = create_sign(sch_rep_1.school.sign, sch_rep_1.school.sign_image, sch_rep_1.school.sign_password, 
                             signatureLine2, contract_path)
        result = create_sign(sch_rep_2.sign, sch_rep_2.sign_image, sch_rep_2.sign_password, signatureLine3, contract_path)
        result = create_sign(sch_rep_2.school.sign, sch_rep_2.school.sign_image, sch_rep_2.school.sign_password, 
                             signatureLine4, contract_path)

        return result, os.path.relpath(contract_path, start=settings.MEDIA_ROOT)
    except:
        return False, None

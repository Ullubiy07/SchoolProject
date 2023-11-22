import datetime
import os
from logging import getLogger

from pathlib import Path

import schedule
import time
from threading import Thread
from django.contrib.auth import logout, login
from django.http import FileResponse, HttpResponseForbidden
from django.urls.base import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.conf import settings
import random
from django.contrib.auth.models import Group, User, Permission
from django.views.generic import TemplateView, CreateView, UpdateView

from EquipApp.models import EquipQuery, EquipBooking
from LectureApp.models import Lecture
from RoomApp.models import RoomBooking, RoomQuery
from main.client import DssClient, SignatureSpec
from main.forms import RegisterUserForm, LoginUserForm, ChangeUserDataForm, ChangePasswordForm, SupplyManagerSignForm, SchoolForm
from main.models import SchRep, Teacher, SupplyManager
from main.utils import DataMixin
import httpx


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


class ChangeSupplyManagerSign(PermissionRequiredMixin, DataMixin, UpdateView):
    permission_required = SupplyManager.Permission
    form_class = SupplyManagerSignForm
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
        return self.request.user.supplymanager


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


def create_supply_manager_user(request):
    if request.user.has_perm(SchRep.Permission):
        username, password = generate_random_string(8), generate_random_string(8)
        while User.objects.filter(username=username).exists():
            username, password = generate_random_string(8), generate_random_string(8)
        user = User.objects.create_user(username=username, password=password)
        permission = Permission.objects.get(name=SupplyManager.Permission)
        user.user_permissions.add(permission)
        SupplyManager.objects.create(user=user, school=request.user.schrep.school)
        group = Group.objects.get(name=SupplyManager.Group)
        user.groups.add(group)
        user.save()
        messages.add_message(request, messages.SUCCESS,
                             f'Вы успешно создали аккаунт завхоза. Логин: {username}, Пароль: {password}.'
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
        messages.add_message(request, messages.SUCCESS,
                             f'Вы успешно создали аккаунт учителя. Логин: {username}, Пароль: {password}.'
                             ' Сохраните эту информацию перед закрытием сообщения')
        return redirect('home')
    else:
        return HttpResponseForbidden('Доступ запрещен')


def logout_user(request):
    logout(request)
    return redirect('login')


def install_file(request, file_path):
    try:
        return FileResponse(open(file_path, 'rb'))
    except:
        messages.add_message(request, messages.ERROR, 'Не удается найти файл.')
        return redirect('home')


dss_client = DssClient()

BOX = {
    "ContractTemplate": {
        "school_rep": [240, 440, 80, 340],
        "school": [490, 440, 330, 340],
        "another_school_rep": [240, 320, 80, 220],
        "another_school": [490, 320, 330, 220]
    },
    "EquipContractTemplate": {
        "school_rep": [240, 560, 80, 460],
        "school": [210, 500, 80, 400],
        "another_school_rep": [490, 560, 330, 460],
        "another_school": [460, 500, 330, 400]
    },
    "RoomContractTemplate": {
        "school_rep": [220, 560, 60, 460],
        "school": [440, 560, 310, 460],
        "another_school_rep": [220, 500, 60, 400],
        "another_school": [440, 500, 310, 400]
    }
}

logger = getLogger()

def to_signature_spec(
        name: str,
        credential_id: str,
        strategy_boxing: str,
        boxing: dict
) -> SignatureSpec:
    return SignatureSpec(
        name=name,
        credential_id=credential_id,
        box=boxing[strategy_boxing]
    )


def get_boxing(filename: str):
    return BOX[filename]


def sign_contract(
        contract_path: str,
        first_supply_manager: SupplyManager,
        second_supply_manager: SupplyManager,
        contract_type: str
):
    contract_path = Path(contract_path)

    raw = contract_path.read_bytes()

    boxing = get_boxing(contract_type)

    signature_specs = (
        to_signature_spec(
            name='Представитель школы-владельца',
            credential_id=first_supply_manager.credential_id,
            strategy_boxing="school_rep",
            boxing=boxing
        ),
        to_signature_spec(
            name='Школа-владелец',
            credential_id=first_supply_manager.school.credential_id,
            strategy_boxing="school",
            boxing=boxing
        ),
        to_signature_spec(
            name='Представитель школы-получателя',
            credential_id=second_supply_manager.credential_id,
            strategy_boxing="another_school_rep",
            boxing=boxing
        ),
        to_signature_spec(
            name='Школа-получатель',
            credential_id=second_supply_manager.school.credential_id,
            strategy_boxing="another_school",
            boxing=boxing
        )
    )

    try:
        document_raw = dss_client.sign_docx_document(raw, *signature_specs)

        contract_path = contract_path.with_suffix(".pdf")

        contract_path.write_bytes(document_raw)

        return True, os.path.relpath(contract_path.absolute(), start=settings.MEDIA_ROOT)
    except Exception as e:
        logger.error("Error signing document", exc_info=e)
        return False, None

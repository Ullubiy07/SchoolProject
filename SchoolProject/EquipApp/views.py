from django.http.response import HttpResponseNotFound
from django.urls.base import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from docxtpl import DocxTemplate
from django.conf import settings
import os

from .forms import *
from .models import *
from main.models import *
from .utils import *
from main.utils import DataMixin
from main.views import generate_random_string, sign_contract

week_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

def render_contract(sch_rep_1, equip_query, equip_booking_id):
    try:
        template = os.path.join(settings.STATIC_ROOT, "main/other/ContractTemplate.docx")

        # Генерируем название файла
        contract_path = os.path.join(settings.MEDIA_ROOT, f"contracts/contract-{generate_random_string(10)}.docx")
        while os.path.exists(contract_path):
            contract_path = os.path.join(settings.MEDIA_ROOT, f"contracts/contract-{generate_random_string(10)}.docx")

        # Создаем директорию, если ее нет
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'contracts')):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'contracts'))

        full_name_1 = sch_rep_1.user.get_full_name()
        if full_name_1 == '':
            full_name_1 = "имя и фамилия не указаны"
        full_name_2 = equip_query.sch_rep.user.get_full_name()
        if full_name_2 == '':
            full_name_2 = "имя и фамилия не указаны"
        
        doc = DocxTemplate(template)
        context = {'id': equip_booking_id, 'current_date': datetime.date.today(), 
                    'sch_rep_1': full_name_1, 'sch_rep_2': full_name_2,
                    'school_1': equip_query.equip.owner, 'school_2': equip_query.sender,
                    'name': equip_query.equip.name, 'quantity': equip_query.quantity,
                    'booking_begin': equip_query.booking_begin, 'booking_end': equip_query.booking_end,
                    'type': 'оборудование'}
        doc.render(context)
        doc.save(contract_path)

        return contract_path
    except:
        return

class EquipQueryList(PermissionRequiredMixin, DataMixin, ListView):
    permission_required = SchRep.Permission
    template_name = "main/table.html"
    model = EquipQuery
    context_object_name = 'equip_query_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Список запросов')

        table = []
        for equip_query in context["equip_query_list"]:
            table.append([
                {"type": "text", "text": equip_query.sender},
                {"type": "link", "text": "Ответить", "link": equip_query.get_respond_url()},
                {"type": "link", "text": equip_query.equip.name, "link": equip_query.equip.get_absolute_url()},
                {"type": "text", "text": equip_query.quantity},
                {"type": "text", "text": equip_query.booking_begin},
                {"type": "text", "text": equip_query.booking_end},
            ])
        context["table"] = table
        context["title_text"] = "Запросы к вашей школе"
        context["link"] = reverse("my_equip_query_list")
        context["link_text"] = "Посмотреть запросы от моей школы"
        if table:
            context["table_head"] = ["Отправитель", "Ответить", "Оборудование", 
                                     "Количество", "Начало брони", "Конец брони"]
        else:
            context["text"] = "К вашей школе запросы не посылались"

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        equip_set = Equipment.objects.filter(owner=self.request.user.schrep.school)
        return EquipQuery.objects.filter(equip__in=equip_set)

class MyEquipQueryList(EquipQueryList):
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        
        context["table_head"] = ["Получатель", "Изменить", "Удалить", "Оборудование",
                                 "Количество", "Начало брони", "Конец брони"]
        table = []
        for equip_query in context["equip_query_list"]:
            table.append([
                {"type": "text", "text": equip_query.equip.owner},
                {"type": "link", "text": "Изменить", "link": reverse('edit_equip_query', kwargs={'query_id': equip_query.pk})},
                {"type": "link", "text": "Удалить", "link": reverse('delete_equip_query', kwargs={'query_id': equip_query.pk})},
                {"type": "link", "text": equip_query.equip.name, "link": equip_query.equip.get_absolute_url()},
                {"type": "text", "text": equip_query.quantity},
                {"type": "text", "text": equip_query.booking_begin},
                {"type": "text", "text": equip_query.booking_end},
            ])
        context["table"] = table
        context["title_text"] = "Запросы от вашей школы"
        context["link"] = reverse("equip_query_list")
        context["link_text"] = "Посмотреть запросы к моей школе"
        if table is None:
            context["text"] = "От вашей школе запросы не посылались"

        return context

    def get_queryset(self):
        return EquipQuery.objects.filter(sender=self.request.user.schrep.school)

class EquipBookingList(LoginRequiredMixin, DataMixin, ListView):
    model = EquipBooking
    template_name = 'main/table.html'
    context_object_name = 'equip_booking_list'
    login_url = reverse_lazy('login')
    pk_url_kwarg = "equip_id"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Список брони')

        equip = get_object_or_404(Equipment, pk=self.kwargs['equip_id'])
        table = []
        for equip_booking in context["equip_booking_list"]:
            table.append([
                {"type": "text", "text": equip_booking.temp_owner},
                {"type": "text", "text": equip_booking.quantity},
                {"type": "text", "text": equip_booking.booking_begin},
                {"type": "text", "text": equip_booking.booking_end},
                {"type": "link", "text": "Договор", "link": reverse("install_file", kwargs={'file_path': equip_booking.contract.path})},
            ])
        context["table"] = table
        context["title_text"] = f"Список бронирования оборудования {equip.name}"
        context["link"] = equip.get_absolute_url()
        context["link_text"] = "К оборудованию"
        if table:
            context["table_head"] = ["Временный владелец", "Количество", "Начало брони", "Конец брони", "Договор"]
        else:
            context["text"] = "Это оборудование никем не забронировано"

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        equip_id = self.kwargs['equip_id']
        return EquipBooking.objects.filter(equip_id=equip_id)

class MyEquipBookingList(PermissionRequiredMixin, DataMixin, ListView):
    permission_required = SchRep.Permission
    model = EquipBooking
    template_name = 'main/table.html'
    context_object_name = 'equip_booking_list'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Бронирования школы')
        table = []
        for equip_booking in context["equip_booking_list"]:
            table.append([
                {"type": "link", "text": equip_booking.equip.name, "link": reverse("equip", kwargs={'equip_id': equip_booking.equip.pk})},
                {"type": "text", "text": equip_booking.quantity},
                {"type": "text", "text": equip_booking.booking_begin},
                {"type": "text", "text": equip_booking.booking_end},
                {"type": "link", "text": "Договор", "link": reverse("install_file", kwargs={'file_path': equip_booking.contract.path})},
            ])
        context["table"] = table
        context["title_text"] = f"Список оборудования, забронированного вашей школой"
        if table:
            context["table_head"] = ["Оборудование", "Количество", "Начало брони", "Конец брони", "Договор"]
        else:
            context["text"] = "Ваша школа не бронировала оборудование"

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return EquipBooking.objects.filter(temp_owner=self.request.user.schrep.school)

class EquipSchedule(LoginRequiredMixin, DataMixin, DetailView):
    model = Equipment
    template_name = 'main/table.html'
    context_object_name = 'equip'
    login_url = reverse_lazy('login')
    pk_url_kwarg = "equip_id"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Расписание оборудования')

        equip = context["equip"]
        table = []
        for weekday in equip.schedule:
            for elem in equip.schedule[weekday]:
                table.append([
                    {"type": "text", "text": week_days[int(weekday)]},
                    {"type": "text", "text": elem[0]},
                    {"type": "text", "text": elem[1]},
                    {"type": "text", "text": elem[2]},
                ])
        context["table"] = table
        context["title_text"] = f"Расписание оборудования {equip.name}"
        context["link"] = equip.get_absolute_url()
        context["link_text"] = "К оборудованию"
        if table:
            context["table_head"] = ["День недели", "Время начала удержания", "Время конца удержания", "Количество"]
        else:
            context["text"] = "У этого оборудования нет расписания"

        return dict(list(context.items()) + list(c_def.items()))

class EquipList(LoginRequiredMixin, DataMixin, ListView):
    model = Equipment
    template_name = 'EquipApp/equip_list.html'
    context_object_name = 'equip_list'
    login_url = reverse_lazy('login')
    mode = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.has_perm(SchRep.Permission):
            context["mode"] = "Просмотр"
        else:
            context["mode"] = self.mode
        c_def = self.get_user_context(title='Список оборудования')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        user = self.request.user
        if user.has_perm(SchRep.Permission):
            return Equipment.objects.exclude(owner=user.schrep.school)
        else:
            return Equipment.objects.all()

class MyEquipList(PermissionRequiredMixin, EquipList):
    permission_required = SchRep.Permission

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['link'] = reverse('equip_list')
        context['link_text'] = "Посмотреть общий список оборудования"
        context['title_text'] = "Список оборудования моей школы"
        if not context["equip_list"]:
            context['title_text'] = "Список оборудования вашей школы пуст..."
        return context

    def get_queryset(self):
        return Equipment.objects.filter(owner=self.request.user.schrep.school)

class RespondEquipQuery(PermissionRequiredMixin, DataMixin, DeleteView):
    permission_required = SchRep.Permission
    model = Equipment
    template_name = 'main/respond_query.html'
    pk_url_kwarg = "query_id"
    success_url = reverse_lazy('equip_query_list')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ответить на запрос')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        equip_set = Equipment.objects.filter(owner=self.request.user.schrep.school)
        return EquipQuery.objects.filter(equip__in=equip_set)
    
    def post(self, request, *args, **kwargs):
        if "Accept" in request.POST:
            equip_query = EquipQuery.objects.get(pk = kwargs["query_id"])
            possible_quantity = equip_query.equip.get_quantity_on_interval(equip_query.booking_begin, equip_query.booking_end)
            if possible_quantity >= equip_query.quantity:
                equip_booking = EquipBooking.objects.create(equip=equip_query.equip, quantity=equip_query.quantity,
                                                            booking_begin=equip_query.booking_begin,
                                                            booking_end=equip_query.booking_end,
                                                            temp_owner=equip_query.sender)
                contract = render_contract(request.user.schrep, equip_query, equip_booking.pk)
                result, contract = sign_contract(contract, request.user.schrep, equip_query.sch_rep)
                if contract:
                    equip_booking.contract = contract
                    equip_booking.save()
                    if result:
                        messages.add_message(request, messages.SUCCESS, 'Вы приняли запрос.')
                    else:
                        messages.add_message(request, messages.WARNING, 
                        'Вы приняли запрос, однако некоторые подписи не могут быть обработаны. Проверьте договор.')
                else:
                    messages.add_message(request, messages.ERROR, 'Произошла ошибка при подписании документа. Проверьте подписи.')
            else:
                messages.add_message(request, messages.WARNING, 
                'Вы не можете принять запрос, т.к оборудования не хватает. Запрос был автоматически отклонен.')
        else:
            messages.add_message(request, messages.ERROR, 'Вы отклонили запрос.')
        return super().post(request, args, kwargs)

class AddEquipQuery(PermissionRequiredMixin, DataMixin, CreateView):
    permission_required = SchRep.Permission
    form_class = EquipQueryForm
    template_name = 'main/form.html'
    pk_url_kwarg = "equip_id"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Запросить оборудование"
        context["button_text"] = "Отправить"

        c_def = self.get_user_context(title='Запросить оборудование')
        return dict(list(context.items()) + list(c_def.items()))

    def dispatch(self, request, *args, **kwargs):
        equip = get_object_or_404(Equipment, pk=kwargs["equip_id"])
        self.initial["equip"] = equip
        self.equip = equip
        if not request.user.has_perm(SchRep.Permission):
            return HttpResponseNotFound("<h1>Страница не доступна<h1>")
        elif equip.owner == request.user.schrep.school:
            return HttpResponseNotFound("<h1>Страница не доступна<h1>")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.sender = self.request.user.schrep.school
        self.object.sch_rep = self.request.user.schrep
        self.object.equip = self.equip
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно отправили запрос.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')

class EditEquipQuery(EquipQueryOwnerPermMixin, DataMixin, UpdateView):
    permission_required = SchRep.Permission
    model = EquipQuery
    form_class = EquipQueryForm
    pk_url_kwarg = "query_id"
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Изменить запрос"
        context["button_text"] = "Сохранить"
        c_def = self.get_user_context(title='Изменить запрос')
        return dict(list(context.items()) + list(c_def.items()))

    def dispatch(self, request, *args, **kwargs):
        equip_query = get_object_or_404(EquipQuery, pk=kwargs["query_id"])
        self.initial["equip"] = equip_query.equip
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили параметры запроса.')
        return super().form_valid(form)


    def get_success_url(self):
        return reverse("my_equip_query_list")

class DeleteEquipQuery(EquipQueryOwnerPermMixin, DataMixin, DeleteView):
    permission_required = SchRep.Permission
    model = EquipQuery
    pk_url_kwarg = "query_id"
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Удалить запрос"
        context["text"] = "Вы точно хотите удалить запрос?"
        context["button_text"] = "Да"
        c_def = self.get_user_context(title='Удалить запрос')
        return dict(list(context.items()) + list(c_def.items()))
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно удалили запрос запроса.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("my_equip_query_list")


class ShowEquip(LoginRequiredMixin, DataMixin, DetailView):
    model = Equipment
    template_name = "EquipApp/equip_details.html"
    pk_url_kwarg = "equip_id"
    context_object_name = "equip"
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
       
        equip = context["equip"]
        user = self.request.user
        if not user.has_perm(SchRep.Permission):
            context["mode"] = "Просмотр"
        elif user.schrep.school == equip.owner:
            context["mode"] = "Владелец"
        else:
            context['mode'] = "Действие"
        
        c_def = self.get_user_context(title=equip.name)
        return dict(list(context.items()) + list(c_def.items()))

class AddEquip(PermissionRequiredMixin, DataMixin, CreateView):
    permission_required = SchRep.Permission
    form_class = EquipForm
    template_name = 'main/form.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Добавить оборудование"
        context["button_text"] = "Добавить"
        c_def = self.get_user_context(title='Добавить оборудование')
        return dict(list(context.items()) + list(c_def.items()))
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user.schrep.school
        if form.cleaned_data["schedule_file"]:
            self.object.schedule = form.cleaned_data["schedule_file"]
        else:
            self.object.schedule = {}
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно добавили оборудование на учет.')
        return super().form_valid(form)

class EditEquip(EquipOwnerPermMixin, DataMixin, UpdateView):
    model = Equipment
    form_class = EquipForm
    pk_url_kwarg = "equip_id"
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Изменить параметры оборудования"
        context["button_text"] = "Сохранить"
        c_def = self.get_user_context(title='Изменить оборудование')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if form.cleaned_data["schedule_file"] is not None:
            self.object.schedule = form.cleaned_data["schedule_file"]
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили параметры оборудования.')
        return super().form_valid(form)

class DeleteEquip(EquipOwnerPermMixin, DataMixin, DeleteView):
    model = Equipment
    template_name = 'main/form.html'
    pk_url_kwarg = "equip_id"
    success_url = reverse_lazy('my_equip_list')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Удалить оборудование"
        context["button_text"] = "Да"
        context["text"] = "Вы точно хотите удалить оборудование?"
        c_def = self.get_user_context(title='Удалить оборудование')
        return dict(list(context.items()) + list(c_def.items()))

    def post(self, request, *args, **kwargs):
        equip_booking = EquipBooking.objects.filter(equip_id=kwargs["equip_id"])
        if equip_booking:
            messages.add_message(request, messages.ERROR, 'Вы не можете удалить оборудование, т.к. оно кем-то забронировано.')
            return redirect('my_equip_list')
        else:
            messages.add_message(request, messages.SUCCESS, 'Вы успешно удалили оборудование с учета.')
            return super().post(request, *args, **kwargs)

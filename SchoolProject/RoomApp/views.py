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
from main.views import sign_contract, generate_random_string

week_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

def render_contract(sch_rep_1, room_query, room_booking_id):
    try:
        template = os.path.join(settings.STATIC_ROOT, "main/other/ContractTemplate.docx")

        contract_path = os.path.join(settings.MEDIA_ROOT, f"contracts/contract-{room_booking_id}.docx")

        # Создаем директорию, если ее нет
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'contracts')):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'contracts'))

        full_name_1 = sch_rep_1.user.get_full_name()
        if full_name_1 == '':
            full_name_1 = "имя и фамилия не указаны"
        full_name_2 = room_query.sch_rep.user.get_full_name()
        if full_name_2 == '':
            full_name_2 = "имя и фамилия не указаны"
        
        doc = DocxTemplate(template)
        context = {'id': room_booking_id, 'current_date': datetime.date.today(), 
                    'sch_rep_1': full_name_1, 'sch_rep_2': full_name_2,
                    'school_1': room_query.room.owner, 'school_2': room_query.sender,
                    'name': room_query.room.name, 'quantity': room_query.quantity,
                    'booking_begin': room_query.booking_begin, 'booking_end': room_query.booking_end,
                    'type': 'помещение'}
        doc.render(context)
        doc.save(contract_path)

        return contract_path
    except:
        return

class RoomQueryList(PermissionRequiredMixin, DataMixin, ListView):
    permission_required = SchRep.Permission
    template_name = "main/table.html"
    model = RoomQuery
    context_object_name = 'room_query_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Список запросов')

        table = []
        for room_query in context["room_query_list"]:
            table.append([
                {"type": "text", "text": room_query.sender},
                {"type": "link", "text": "Ответить", "link": room_query.get_respond_url()},
                {"type": "link", "text": room_query.room.name, "link": room_query.room.get_absolute_url()},
                {"type": "text", "text": room_query.quantity},
                {"type": "text", "text": room_query.booking_begin},
                {"type": "text", "text": room_query.booking_end},
            ])
        context["table"] = table
        context["title_text"] = "Запросы к вашей школе"
        context["link"] = reverse("my_room_query_list")
        context["link_text"] = "Посмотреть запросы от моей школы"
        if table:
            context["table_head"] = ["Отправитель", "Ответить", "Помещение", 
                                     "Количество", "Начало брони", "Конец брони"]
        else:
            context["text"] = "К вашей школе запросы не посылались"

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        room_set = Room.objects.filter(owner=self.request.user.schrep.school)
        return RoomQuery.objects.filter(room__in=room_set)

class MyRoomQueryList(RoomQueryList):
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        
        context["table_head"] = ["Получатель", "Изменить", "Удалить", "Помещение",
                                 "Количество", "Начало брони", "Конец брони"]
        table = []
        for room_query in context["room_query_list"]:
            table.append([
                {"type": "text", "text": room_query.room.owner},
                {"type": "link", "text": "Изменить", "link": reverse('edit_room_query', kwargs={'query_id': room_query.pk})},
                {"type": "link", "text": "Удалить", "link": reverse('delete_room_query', kwargs={'query_id': room_query.pk})},
                {"type": "link", "text": room_query.room.name, "link": room_query.room.get_absolute_url()},
                {"type": "text", "text": room_query.quantity},
                {"type": "text", "text": room_query.booking_begin},
                {"type": "text", "text": room_query.booking_end},
            ])
        context["table"] = table
        context["title_text"] = "Запросы от вашей школы"
        context["link"] = reverse("room_query_list")
        context["link_text"] = "Посмотреть запросы к моей школе"
        if table is None:
            context["text"] = "От вашей школе запросы не посылались"

        return context

    def get_queryset(self):
        return RoomQuery.objects.filter(sender=self.request.user.schrep.school)

class RoomBookingList(LoginRequiredMixin, DataMixin, ListView):
    model = RoomBooking
    template_name = 'main/table.html'
    context_object_name = 'room_booking_list'
    login_url = reverse_lazy('login')
    pk_url_kwarg = "room_id"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Список брони')

        room = get_object_or_404(Room, pk=self.kwargs['room_id'])
        table = []
        for room_booking in context["room_booking_list"]:
            table.append([
                {"type": "text", "text": room_booking.temp_owner},
                {"type": "text", "text": room_booking.quantity},
                {"type": "text", "text": room_booking.booking_begin},
                {"type": "text", "text": room_booking.booking_end},
                {"type": "link", "text": "Договор", "link": room_booking.contract.url}
            ])
        context["table"] = table
        context["title_text"] = f"Список бронирования помещения {room.name}"
        context["link"] = room.get_absolute_url()
        context["link_text"] = "К помещению"
        if table:
            context["table_head"] = ["Временный владелец", "Количество", "Начало брони", "Конец брони", "Договор"]
        else:
            context["text"] = "Это помещение никем не забронировано"

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return RoomBooking.objects.filter(room_id=room_id)

class MyRoomBookingList(PermissionRequiredMixin, DataMixin, ListView):
    permission_required = SchRep.Permission
    model = RoomBooking
    template_name = 'main/table.html'
    context_object_name = 'room_booking_list'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Бронирования школы')
        table = []
        for room_booking in context["room_booking_list"]:
            table.append([
                {"type": "link", "text": room_booking.room.name, "link": reverse("room", kwargs={'room_id': room_booking.room.pk})},
                {"type": "text", "text": room_booking.quantity},
                {"type": "text", "text": room_booking.booking_begin},
                {"type": "text", "text": room_booking.booking_end},
                {"type": "link", "text": "Договор", "link": room_booking.contract.url}
            ])
        context["table"] = table
        context["title_text"] = f"Список помещений, забронированного вашей школой"
        if table:
            context["table_head"] = ["Помещение", "Количество", "Начало брони", "Конец брони", "Договор"]
        else:
            context["text"] = "Ваша школа не бронировала помещения"

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return RoomBooking.objects.filter(temp_owner=self.request.user.schrep.school)

class RoomSchedule(LoginRequiredMixin, DataMixin, DetailView):
    model = Room
    template_name = 'main/table.html'
    context_object_name = 'room'
    login_url = reverse_lazy('login')
    pk_url_kwarg = "room_id"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Расписание помещения')

        room = context["room"]
        table = []
        for weekday in room.schedule:
            for elem in room.schedule[weekday]:
                table.append([
                    {"type": "text", "text": week_days[int(weekday)]},
                    {"type": "text", "text": elem[0]},
                    {"type": "text", "text": elem[1]},
                    {"type": "text", "text": elem[2]},
                ])
        context["table"] = table
        context["title_text"] = f"Расписание помещения {room.name}"
        context["link"] = room.get_absolute_url()
        context["link_text"] = "К помещению"
        if table:
            context["table_head"] = ["День недели", "Время начала удержания", "Время конца удержания", "Количество"]
        else:
            context["text"] = "У этого помещения нет расписания"

        return dict(list(context.items()) + list(c_def.items()))

class RoomList(LoginRequiredMixin, DataMixin, ListView):
    model = Room
    template_name = 'RoomApp/room_list.html'
    context_object_name = 'room_list'
    login_url = reverse_lazy('login')
    mode = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not user.has_perm(SchRep.Permission):
            context["mode"] = "Просмотр"
        else:
            context["mode"] = self.mode
        c_def = self.get_user_context(title='Список помещений')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        user = self.request.user
        if user.has_perm(SchRep.Permission):
            return Room.objects.exclude(owner=user.schrep.school)
        else:
            return Room.objects.all()

class MyRoomList(PermissionRequiredMixin, RoomList):
    permission_required = SchRep.Permission

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['link'] = reverse('room_list')
        context['link_text'] = "Посмотреть общий список помещений"
        context['title_text'] = "Список помещений моей школы"
        if not context["room_list"]:
            context['title_text'] = "Список помещений вашей школы пуст..."
        return context

    def get_queryset(self):
        return Room.objects.filter(owner=self.request.user.schrep.school)


class RespondRoomQuery(PermissionRequiredMixin, DataMixin, DeleteView):
    permission_required = SchRep.Permission
    model = Room
    template_name = 'main/respond_query.html'
    pk_url_kwarg = "query_id"
    success_url = reverse_lazy('room_query_list')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ответить на запрос')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        room_set = Room.objects.filter(owner=self.request.user.schrep.school)
        return RoomQuery.objects.filter(room__in=room_set)
    
    def post(self, request, *args, **kwargs):
        if "Accept" in request.POST:
            try:
                room_query = RoomQuery.objects.get(pk = kwargs["query_id"])
                possible_quantity = room_query.room.get_quantity_on_interval(room_query.booking_begin, room_query.booking_end)
                if possible_quantity >= room_query.quantity:
                    room_booking = RoomBooking.objects.create(room=room_query.room, quantity=room_query.quantity,
                                                                booking_begin=room_query.booking_begin,
                                                                booking_end=room_query.booking_end,
                                                                temp_owner=room_query.sender)
                    contract = render_contract(request.user.schrep, room_query, room_booking.pk)
                    result, contract = sign_contract(contract, request.user.schrep, room_query.sch_rep)
                    room_booking.contract = contract
                    room_booking.save()
                    if result:
                        messages.add_message(request, messages.SUCCESS, 'Вы приняли запрос.')
                    else:
                        messages.add_message(request, messages.WARNING, 
                        'Вы приняли запрос, однако некоторые подписи не могут быть обработаны. Проверьте договор.')
                else:
                    messages.add_message(request, messages.WARNING, 
                    'Вы не можете принять запрос, т.к помещений не хватает. Запрос был автоматически отклонен.')
            except:
                messages.add_message(request, messages.ERROR, 'Произошла ошибка при подписании документа. Проверьте подписи.')
                return super().post(request, args, kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'Вы отклонили запрос.')
        return super().post(request, args, kwargs)

class AddRoomQuery(PermissionRequiredMixin, DataMixin, CreateView):
    permission_required = SchRep.Permission
    form_class = RoomQueryForm
    template_name = 'main/form.html'
    pk_url_kwarg = "room_id"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Запросить помещение"
        context["button_text"] = "Отправить"

        c_def = self.get_user_context(title='Запросить помещение')
        return dict(list(context.items()) + list(c_def.items()))

    def dispatch(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=kwargs["room_id"])
        self.initial["room"] = room
        self.room = room
        if not request.user.has_perm(SchRep.Permission):
            return HttpResponseNotFound("<h1>Страница не доступна<h1>")
        elif room.owner == request.user.schrep.school:
            return HttpResponseNotFound("<h1>Страница не доступна<h1>")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.sender = self.request.user.schrep.school
        self.object.sch_rep = self.request.user.schrep
        self.object.room = self.room
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно отправили запрос.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')

class EditRoomQuery(RoomQueryOwnerPermMixin, DataMixin, UpdateView):
    permission_required = SchRep.Permission
    model = RoomQuery
    form_class = RoomQueryForm
    pk_url_kwarg = "query_id"
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Изменить запрос"
        context["button_text"] = "Сохранить"
        c_def = self.get_user_context(title='Изменить запрос')
        return dict(list(context.items()) + list(c_def.items()))

    def dispatch(self, request, *args, **kwargs):
        room_query = get_object_or_404(RoomQuery, pk=kwargs["query_id"])
        self.initial["room"] = room_query.room
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили параметры запроса.')
        return super().form_valid(form)


    def get_success_url(self):
        return reverse("my_room_query_list")

class DeleteRoomQuery(RoomQueryOwnerPermMixin, DataMixin, DeleteView):
    permission_required = SchRep.Permission
    model = RoomQuery
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
        return reverse("my_room_query_list")


class ShowRoom(LoginRequiredMixin, DataMixin, DetailView):
    model = Room
    template_name = "RoomApp/room_details.html"
    pk_url_kwarg = "room_id"
    context_object_name = "room"
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
       
        room = context["room"]
        user = self.request.user
        if not user.has_perm(SchRep.Permission):
            context["mode"] = "Просмотр"
        elif user.schrep.school == room.owner:
            context["mode"] = "Владелец"
        else:
            context['mode'] = "Действие"
        
        c_def = self.get_user_context(title=room.name)
        return dict(list(context.items()) + list(c_def.items()))

class AddRoom(PermissionRequiredMixin, DataMixin, CreateView):
    permission_required = SchRep.Permission
    form_class = RoomForm
    template_name = 'main/form.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Добавить помещение"
        context["button_text"] = "Добавить"
        c_def = self.get_user_context(title='Добавить помещение')
        return dict(list(context.items()) + list(c_def.items()))
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user.schrep.school
        if form.cleaned_data["schedule_file"]:
            self.object.schedule = form.cleaned_data["schedule_file"]
        else:
            self.object.schedule = {}
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно добавили помещение на учет.')
        return super().form_valid(form)

class EditRoom(RoomOwnerPermMixin, DataMixin, UpdateView):
    model = Room
    form_class = RoomForm
    pk_url_kwarg = "room_id"
    template_name = 'main/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Изменить параметры помещения"
        context["button_text"] = "Сохранить"
        c_def = self.get_user_context(title='Изменить помещение')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if form.cleaned_data["schedule_file"] is not None:
            self.object.schedule = form.cleaned_data["schedule_file"]
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Вы успешно изменили параметры помещения.')
        return super().form_valid(form)

class DeleteRoom(RoomOwnerPermMixin, DataMixin, DeleteView):
    model = Room
    template_name = 'main/form.html'
    pk_url_kwarg = "room_id"
    success_url = reverse_lazy('my_room_list')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_text"] = "Удалить помещение"
        context["button_text"] = "Да"
        context["text"] = "Вы точно хотите удалить помещение?"
        c_def = self.get_user_context(title='Удалить помещение')
        return dict(list(context.items()) + list(c_def.items()))

    def post(self, request, *args, **kwargs):
        room_booking = RoomBooking.objects.filter(room_id=kwargs["room_id"])
        if room_booking:
            messages.add_message(request, messages.ERROR, 'Вы не можете удалить помещение, т.к. оно кем-то забронировано.')
            return redirect('my_room_list')
        else:
            messages.add_message(request, messages.SUCCESS, 'Вы успешно удалили помещение с учета.')
            return super().post(request, *args, **kwargs)

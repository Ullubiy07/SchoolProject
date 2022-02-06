from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.urls import reverse
from main.models import School, Category, Interval, SchRep
from django.templatetags.static import static
import datetime

class Room(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    quantity = models.SmallIntegerField(verbose_name="Количество")
    size = models.SmallIntegerField(verbose_name="Размер")
    address = models.CharField(max_length=100, verbose_name="Адрес")
    owner = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Владелец")
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default="Без категории", verbose_name="Категория")
    description = models.TextField(max_length=1000, default="Описания нет", verbose_name="Описание")
    image = models.ImageField(upload_to="room_photos", verbose_name="Картинка", null=True, blank=True)
    schedule = models.JSONField(verbose_name="Расписание", default=dict)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('room', kwargs={'room_id': self.pk})

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('main\img\default_image.jpg')

    def get_quantity_on_interval(self, begin, end):
        room_booking_list = RoomBooking.objects.filter(room_id=self.pk)
        
        interval = Interval(begin, end, 0)
        result = []
        for room_booking in room_booking_list:
            booking_interval = Interval(room_booking.booking_begin, room_booking.booking_end, room_booking.quantity)
            intersection = interval + booking_interval
            if intersection:
                if not result:
                    result = intersection
                    continue
                new_result = []
                for elem1 in result:
                    intersection1 = elem1 + intersection[0]
                    if intersection1:
                        new_result += intersection1
                    else:
                        new_result.append(elem1)
                result = new_result
        if not result:
            result.append(interval)
        
        count = 0
        if self.schedule:
            weekdays = []
            for i in range(1, (interval.end.date() - interval.begin.date()).days):
                weekday =  (interval.begin + datetime.timedelta(days=i)).weekday() 
                if weekday != interval.end.weekday() and weekday != interval.begin.weekday():
                    weekdays.append(weekday)
                if len(weekdays) == 5:
                    break
            
            for freeze in self.schedule[str(interval.begin.weekday())]:
                begin_time = list(map(int, freeze[0].split(":")))
                begin = datetime.datetime(interval.begin.year, interval.begin.month, interval.begin.day, 
                                          begin_time[0], begin_time[1])
                end_time = list(map(int, freeze[1].split(":")))
                end = datetime.datetime(interval.begin.year, interval.begin.month, interval.begin.day, 
                                          end_time[0], end_time[1])
                freeze_interval = Interval(begin, end, freeze[2])
                if freeze_interval + interval:
                    count += freeze_interval.quantity
            if interval.begin.weekday() != interval.end.weekday():
                for freeze in self.schedule[str(interval.end.weekday())]:
                    begin_time = list(map(int, freeze[0].split(":")))
                    begin = datetime.datetime(interval.end.year, interval.end.month, interval.end.day, 
                                            begin_time[0], begin_time[1])
                    end_time = list(map(int, freeze[1].split(":")))
                    end = datetime.datetime(interval.end.year, interval.end.month, interval.end.day, 
                                            end_time[0], end_time[1])
                    freeze_interval = Interval(begin, end, freeze[2])
                    if freeze_interval + interval:
                        count += freeze_interval.quantity
            
            for weekday in weekdays:
                for freeze in self.schedule[str(weekday)]:
                    count += freeze[2]

        return max(0, self.quantity - max(result, key=lambda x: x.quantity).quantity - count)

class RoomBooking(models.Model):
    room = ForeignKey("Room", on_delete=models.PROTECT, verbose_name="Помещение")
    quantity = models.SmallIntegerField(verbose_name="Количество")
    booking_begin = models.DateTimeField(verbose_name="Начало брони")
    booking_end = models.DateTimeField(verbose_name="Конец брони")
    temp_owner = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Временный владелец")
    contract = models.FileField(verbose_name="Договор", upload_to="contracts", null=True, blank=True,
                                validators=[FileExtensionValidator(allowed_extensions=['docx'])])

    def __str__(self):
        return f"Бронь: {self.room}"

class RoomQuery(models.Model):
    sender = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Отправитель")
    sch_rep = ForeignKey(SchRep, on_delete=models.CASCADE, verbose_name="Представитель")
    room = ForeignKey("Room", on_delete=models.CASCADE, verbose_name="Помещение")
    quantity = models.SmallIntegerField(verbose_name="Количество")
    booking_begin = models.DateTimeField(verbose_name="Начало брони")
    booking_end = models.DateTimeField(verbose_name="Конец брони")
    
    def __str__(self):
        return f"Запрос помещения от {self.sender} к {self.room.owner}"

    def get_respond_url(self):
        return f"/room_query/{self.pk}/respond"
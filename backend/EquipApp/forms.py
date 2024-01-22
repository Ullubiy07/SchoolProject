
from .models import *
from django import forms
from django.core.exceptions import ValidationError
import datetime
import openpyxl

common_class = "u-border-1 u-border-grey-30 u-input u-input-rectangle u-white"


class EquipForm(forms.ModelForm):
    schedule_file = forms.FileField(label="Расписание", required=False,
                                    widget=forms.FileInput(attrs={'class': common_class}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Категория не выбрана'

    class Meta:
        model = Equipment
        fields = ('name', 'quantity', 'category', 'description', 'image')

        widgets = {
            'name': forms.TextInput(attrs={"class": common_class,
                                           "placeholder":
                                               "Введите название оборудования"}),
            'quantity': forms.NumberInput(attrs={"class": common_class,
                                                 "placeholder": "Введите количество оборудования"}),
            'description': forms.Textarea(attrs={"class": common_class,
                                                 "cols": 60,
                                                 "rows": 10}),
            'category': forms.Select(attrs={"class": common_class}),
            'image': forms.FileInput(attrs={"class": common_class}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > 10000:
            raise ValidationError("Нельзя ставить на учет более 10000 шт. оборудования")
        if quantity <= 0:
            raise ValidationError("Количество должно быть больше нуля")

        return quantity

    def clean_schedule_file(self):
        schedule_file = self.cleaned_data["schedule_file"]

        if schedule_file is None:
            return

        try:
            week_schedule = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
            ws = openpyxl.load_workbook(schedule_file).get_sheet_by_name("Лист1")
            for i in range(6, 107):
                row = ws[f"A{i}": f"H{i}"][0]
                if row[0].value is None:
                    break
                try:
                    interval = row[0].value.split(" - ")
                    begin = interval[0].split(":")
                    begin = datetime.time(int(begin[0]), int(begin[1]))
                    end = interval[1].split(":")
                    end = datetime.time(int(end[0]), int(end[1]))
                    if end == begin:
                        continue
                except:
                    continue
                for cell in row[1:]:
                    if isinstance(cell.value, int):
                        week_schedule[cell.column - 2].append([begin.isoformat(), end.isoformat(), cell.value])
        except:
            raise ValidationError("Неправильный ввод")

        if week_schedule == {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}:
            return {}

        return week_schedule


class EquipQueryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if "equip" in kwargs["initial"]:
            self.equip = kwargs["initial"]["equip"]
        super().__init__(*args, **kwargs)

    class Meta:
        model = EquipQuery
        fields = ('booking_begin', 'booking_end', 'quantity')

        widgets = {
            'quantity': forms.NumberInput(attrs={"class": common_class, "type": "number"}),
            'booking_begin': forms.DateTimeInput(
                attrs={"class": common_class, "type": "datetime", "placeholder": "21.01.2022 17:47"}),
            'booking_end': forms.DateTimeInput(
                attrs={"class": common_class, "type": "datetime", "placeholder": "21.01.2022 17:47"}),
        }

    def clean_booking_begin(self):
        booking_begin = self.cleaned_data["booking_begin"]
        if booking_begin < datetime.datetime.now():
            raise ValidationError("Дата и время начала бронирования должны быть позже текущей даты и времени")
        if booking_begin > (datetime.datetime.now() + datetime.timedelta(days=90)):
            raise ValidationError(
                "Начало бронирования интервала не должно быть позже сегодняшней даты больше чем на 90 дней")

        return booking_begin

    def clean_booking_end(self):
        booking_end = self.cleaned_data["booking_end"]

        if booking_end < datetime.datetime.now():
            raise ValidationError("Дата и время конца бронирования должны быть позже текущей даты и времени")

        if "booking_begin" in self.cleaned_data:
            booking_begin = self.cleaned_data["booking_begin"]
            if booking_begin > booking_end:
                raise ValidationError(
                    "Дата и время конца бронирования должны быть позже даты и времени начала бронирования")
            if (booking_end - booking_begin).days > 90:
                raise ValidationError("Интервал бронирования не должен превышать 90 дней")

        return booking_end

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > 10000:
            raise ValidationError("Слишком большое количество запрашиваемого оборудования. Уменьшите количество.")

        if quantity <= 0:
            raise ValidationError("Количество должно быть больше нуля")

        if "booking_begin" in self.cleaned_data and "booking_end" in self.cleaned_data:
            booking_begin = self.cleaned_data["booking_begin"]
            booking_end = self.cleaned_data["booking_end"]
            equip = self.equip
            possible_quantity = equip.get_quantity_on_interval(booking_begin, booking_end)
            if possible_quantity < quantity:
                raise ValidationError(
                    f"Оборудования на данный период времени не хватает. На данный период доступно {possible_quantity} шт.")

        return quantity


# class EquipAddSchedule(forms.ModelForm):
#     class Meta:
#         model = Equipment
#         fields = ["day_and_time"]
#
#         widgets = {
#             'day_and_time': forms.TextInput(attrs={
#                 'class': 'equip_schedule',
#                 'placeholder': 'Понедельник, 19:40, 20:40'
#             })
#         }

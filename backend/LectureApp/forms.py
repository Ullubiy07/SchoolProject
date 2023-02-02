from .models import *
from django import forms
from django.core.exceptions import ValidationError
import datetime

common_class = "u-border-1 u-border-grey-30 u-input u-input-rectangle u-white"


class LectureForm(forms.ModelForm):
    form = forms.ChoiceField(label="Форма проведения",
                             choices=[["Очно", "Очно"], ["Очно-заочно", "Очно-заочно"], ["Заочно", "Заочно"]],
                             widget=forms.Select(attrs={'class': common_class}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "lecture" in kwargs["initial"]:
            self.lecture = kwargs["initial"]["lecture"]
        self.fields['category'].empty_label = 'Категория не выбрана'
        self.fields['target_audience'].empty_label = 'Целевая аудитория не выбрана'

    class Meta:
        model = Lecture
        fields = ('name', 'category', 'start_datetime', 'description', 'address',
                  'max_places', 'duration', 'target_audience', 'form', 'image')

        widgets = {
            'name': forms.TextInput(attrs={"class": common_class,
                                           "placeholder": "Введите название оборудования"}),
            'address': forms.TextInput(attrs={"class": common_class,
                                              "placeholder": "Введите адрес проведения лекции"}),
            'max_places': forms.NumberInput(attrs={"class": common_class,
                                                   "placeholder": "Введите максимальное кол-во участников"}),
            'target_audience': forms.Select(attrs={"class": common_class}),
            'start_datetime': forms.DateTimeInput(attrs={"class": common_class,
                                                         "placeholder": "Например: 25.01.2022 18:24"}),
            'duration': forms.TimeInput(attrs={"class": common_class,
                                               "placeholder": "Например: 2:30:00"}),
            'description': forms.Textarea(attrs={"class": common_class,
                                                 "cols": 60,
                                                 "rows": 10}),
            'category': forms.Select(attrs={"class": common_class}),
            'image': forms.FileInput(attrs={"class": common_class}),
        }

    def clean_max_places(self):
        max_places = self.cleaned_data["max_places"]
        if max_places > 10000:
            raise ValidationError("В лекции не может учавствовать более 10000 человек")
        if max_places <= 0:
            raise ValidationError("Количество мест должно быть больше нуля")
        if hasattr(self, "lecture"):
            record_quantity = self.lecture.get_record_quantity()
            if max_places < record_quantity:
                raise ValidationError(
                    f"Вы не можете уменьшить максимальное число мест ниже количетсва уже записавшихся людей [{record_quantity}]")

        return max_places

    def clean_start_datetime(self):
        start_datetime = self.cleaned_data["start_datetime"]
        if start_datetime < datetime.datetime.today():
            raise ValidationError("Дата начала леции должна быть позже сегодняшнего дня")
        if start_datetime > (datetime.datetime.today() + datetime.timedelta(days=90)):
            raise ValidationError("Начало лекции не должно быть позже сегодняшней даты более чем на 90 дней")

        return start_datetime

    def clean_duration(self):
        duration = self.cleaned_data["duration"]
        if duration > datetime.timedelta(hours=8):
            raise ValidationError("Лекция не должна длиться более 8 часов")
        if duration < datetime.timedelta(minutes=30):
            raise ValidationError("Лекция не должна длиться менее 30 минут")

        return duration

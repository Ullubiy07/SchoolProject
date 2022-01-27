from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from main.models import Category, Teacher

class TargetAudience(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название", db_index=True)

    def __str__(self):
        return self.name

class LectureRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    lecture = models.ForeignKey("Lecture", on_delete=models.CASCADE, verbose_name="Лекция")

    def __str__(self):
        return f"Запись {self.user} на лекцию {self.lecture}"

class Lecture(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default="Без категории", verbose_name="Категория")
    organizer = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Организатор")
    start_datetime = models.DateTimeField(verbose_name="Дата и время начала")
    description = models.TextField(max_length=1000, default="Описания нет", verbose_name="Описание")
    address = models.CharField(verbose_name="Адрес проведения", max_length=50, null=True)
    max_places = models.SmallIntegerField(verbose_name="Максимальное количество мест")
    duration = models.DurationField(verbose_name="Длительность лекции")
    target_audience = models.ForeignKey("TargetAudience", on_delete=models.SET_DEFAULT, 
                                        default=0, verbose_name="Целевая аудитория")
    form = models.CharField(max_length=20, verbose_name="Форма проведения")
    image = models.ImageField(upload_to="lecture_photos", verbose_name="Картинка", default="default_image.jpg")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('lecture', kwargs={'lecture_id': self.pk})

    def get_quantity_free_places(self):
        return len(LectureRecord.objects.filter(lecture=self))

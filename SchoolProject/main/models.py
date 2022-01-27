from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import ForeignKey, OneToOneField

class School(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    image = models.ImageField(upload_to="school_photos", default="default_image.jpg")
    description = models.TextField(max_length=1000, default="Описания нет")

    def __str__(self):
        return self.name

class SchRep(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    school = ForeignKey("School", on_delete=models.CASCADE)

    Permission = "main.school_rep"
    Group = "Представитель школы"

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    school = ForeignKey("School", on_delete=models.CASCADE)

    Permission = "main.teacher"
    Group = "Учитель"

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)

    def __str__(self):
        return self.name
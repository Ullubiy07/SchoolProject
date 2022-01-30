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
        
class Interval:
    def __init__(self, begin, end, quantity):
        self.begin = begin
        self.end = end
        self.quantity = quantity

    def __str__(self):
        return f"Интервал: {self.begin}, {self.end}, {self.quantity}"

    def __repr__(self):
        return f"Интервал: {self.begin}, {self.end}, {self.quantity}"

    def __add__(self, other):
        if other.begin > self.end or other.end < self.begin:
            return False
        
        min_begin, max_begin = min(self.begin, other.begin), max(self.begin, other.begin)
        min_end, max_end = min(self.end, other.end), max(self.end, other.end)
        begin_quantity = min(self, other, key=lambda x: x.begin).quantity
        end_quantity = max(self, other, key=lambda x: x.end).quantity

        one = Interval(max_begin, min_end, self.quantity + other.quantity)
        two = Interval(min_begin, max_begin, begin_quantity)
        three = Interval(min_end, max_end, end_quantity)

        return [i for i in [one, two, three] if i.begin != i.end and i.begin >= self.begin and i.end <= self.end]
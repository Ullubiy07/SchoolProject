from django.contrib import admin
from django.contrib.auth.models import Permission

from main.models import Category, School, SchRep, Teacher, SupplyManager

admin.site.register(Category)
admin.site.register(School)
admin.site.register(SchRep)
admin.site.register(Teacher)
admin.site.register(Permission)
admin.site.register(SupplyManager)

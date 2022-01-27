from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import *

admin.site.register(Category)
admin.site.register(School)
admin.site.register(SchRep)
admin.site.register(Teacher)
admin.site.register(Permission)
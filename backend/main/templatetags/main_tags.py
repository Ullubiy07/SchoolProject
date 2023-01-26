import sched
from django import template
from main.models import *

register = template.Library()

@register.simple_tag()
def get_mess_class(type):
    if type == "error":
        mess_class = "alert"
    elif type == "success":
        mess_class = "alert success"
    elif type == "warning":
        mess_class = "alert warning"
    else:
        mess_class = "alert info"
    return mess_class

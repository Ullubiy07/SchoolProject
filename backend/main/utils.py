from django.http import HttpRequest
from django.http.response import HttpResponseForbidden
from .models import SchRep, Teacher

"""
Уровни доступа:
    0 - Не авторизован;
    1 - Авторизован;
    2 - Учитель;
    3 - Школьный представитель;
"""

main_menu = [
    {"title": "Главная", "url_name": "home", "access_levels": [0, 1, 2, 3]},

    {"title": "Вход/Регистрация", "access_levels": [0], "url_name": None,
     "submenu": [{"title": "Вход", "access_levels": [0], "url_name": "login"},
                 {"title": "Регистрация", "access_levels": [0], "url_name": "register"}
                 ]},

    {"title": "Каталоги", "access_levels": [1, 2, 3], "url_name": None,
     "submenu": [{"title": "Оборудование", "access_levels": [1, 2, 3], "url_name": "equip_list"},
                 {"title": "Помещение", "access_levels": [1, 2, 3], "url_name": "room_list"},
                 {"title": "Лекции", "access_levels": [1, 2, 3], "url_name": "lecture_list"}
                 ]},

    {"title": "Запросы", "access_levels": [3], "url_name": None,
     "submenu": [{"title": "Оборудование", "access_levels": [3], "url_name": "equip_query_list"},
                 {"title": "Помещение", "access_levels": [3], "url_name": "room_query_list"}
                 ]},

    {"title": "Бронирования школы", "access_levels": [3], "url_name": None,
     "submenu": [{"title": "Оборудование", "access_levels": [3], "url_name": "my_equip_booking_list"},
                 {"title": "Помещение", "access_levels": [3], "url_name": "my_room_booking_list"}
                 ]},

    {"title": "Личный кабинет", "access_levels": [1, 2, 3], "url_name": None,
     "submenu": [{"title": "Изменить данные аккаунта", "access_levels": [1, 2, 3], "url_name": "edit_user_data"},
                 {"title": "Изменить пароль", "access_levels": [1, 2, 3], "url_name": "change_password"},
                 {"title": "Изменить свою подпись", "access_levels": [3], "url_name": "change_sch_rep_sign"},
                 {"title": "Изменить данные школы", "access_levels": [3], "url_name": "change_school_data"},
                 {"title": "Создать аккаунт представителя", "access_levels": [3], "url_name": "create_sch_rep_user"},
                 {"title": "Создать аккаунт учителя", "access_levels": [3], "url_name": "create_teacher"},
                 {"title": "Выйти", "access_levels": [1, 2, 3], "url_name": "logout"}
                 ]},
]


class DataMixin:
    request: HttpRequest

    def get_user_context(self, **kwargs):
        context = kwargs

        access_level = 0
        if self.request.user.is_authenticated:
            access_level = 1
        if self.request.user.has_perm(Teacher.Permission):
            access_level = 2
        if self.request.user.has_perm(SchRep.Permission):
            access_level = 3

        user_menu = []
        for elem in main_menu:
            cur_elem = elem.copy()
            if access_level in elem["access_levels"]:
                if "submenu" in elem:
                    submenu = []
                    for sub_elem in elem["submenu"]:
                        if access_level in sub_elem["access_levels"]:
                            submenu.append(sub_elem)
                    cur_elem["submenu"] = submenu
                user_menu.append(cur_elem)

        context['main_menu'] = user_menu

        return context


class OwnerPermMixin:
    def dispatch(self, request, *args, **kwargs):
        owner = self.get_owner(kwargs)
        if not request.user.has_perm(SchRep.Permission):
            return HttpResponseForbidden("<h1>Страница не доступна<h1>")
        elif owner != request.user.schrep.school:
            return HttpResponseForbidden("<h1>Страница не доступна<h1>")
        return super().dispatch(request, *args, **kwargs)

    def get_owner(self, kwargs):
        return None

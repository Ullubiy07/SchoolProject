from django.urls import path
from .views import *

urlpatterns = [
    path('lecture_list/', LectureList.as_view(mode='Действие'), name="lecture_list"),
    path('my_lecture_list/', MyLectureList.as_view(mode='Владелец'), name="my_lecture_list"),

    path('lecture/<int:lecture_id>/', ShowLecture.as_view(), name='lecture'),
]
from django.urls import path
from .views import *

urlpatterns = [
    path('lecture_list/', LectureList.as_view(mode='Действие'), name="lecture_list"),
    path('my_lecture_list/', MyLectureList.as_view(mode='Владелец'), name="my_lecture_list"),

    path('lecture/<int:lecture_id>/', ShowLecture.as_view(), name='lecture'),
    path('lecture/<int:lecture_id>/edit/', EditLecture.as_view(), name="edit_lecture"),
    path('lecture/<int:lecture_id>/delete/', DeleteLecture.as_view(), name="delete_lecture"),
    path('lecture/<int:lecture_id>/create_record/', create_lecture_record, name="create_lecture_record"),
    path('lecture/add/', AddLecture.as_view(), name="add_lecture"),
    path('lecture_search/', LectureSearch.as_view(), name='lecture_search')
]
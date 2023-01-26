from django.urls import path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('login/', LoginUser.as_view(), name='login'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('create_sch_rep_user/', create_sch_rep_user, name='create_sch_rep_user'),
    path('create_teacher/', create_teacher, name='create_teacher'),
    path('edit_user_data/', ChangeUserData.as_view(), name='edit_user_data'),

    path('change_sch_rep_sign/', ChangeSchRepSign.as_view(), name='change_sch_rep_sign'),
    path('change_school_data/', ChangeSchoolData.as_view(), name='change_school_data'),

    path('install_file/<path:file_path>/', install_file, name="install_file"),
]
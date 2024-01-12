from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("server.main.urls")),
    path('', include("server.EquipApp.urls")),
    path('', include("server.RoomApp.urls")),
    path('', include("server.LectureApp.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]

if settings.DEBUG:
        urlpatterns += (
            static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
            static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        )

handler404 = 'server.EquipApp.views.error_404'

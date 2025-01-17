from django.contrib import admin
from django.urls import path, include

# Til qo'shish
from django.views.i18n import set_language

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include("ombor.urls")),
    path('i18n/',set_language, name='set_language'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
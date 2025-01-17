# urls.py
from django.urls import path
from .views import kirdi_upload_view

urlpatterns = [
    path('admin/kirdi-upload/', kirdi_upload_view, name='kirdi_upload'),
]

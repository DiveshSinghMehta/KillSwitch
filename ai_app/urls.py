from django.urls import path
from .views import ask, add_document, kill_service, kill_status, reset_service

urlpatterns = [
    path("ask/", ask),
    path("documents/", add_document),
    path("admin/kill/", kill_service),
    path("admin/status/", kill_status),
    path("admin/reset/", reset_service),
]

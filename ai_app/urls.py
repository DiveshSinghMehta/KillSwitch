from django.urls import path
from .views import ask, add_document

urlpatterns = [
    path("ask/", ask),
    path("documents/", add_document),
]
from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path("", views.note_list, name="note_list"),
    path("<int:pk>/delete/", views.note_delete, name="note_delete"),
]

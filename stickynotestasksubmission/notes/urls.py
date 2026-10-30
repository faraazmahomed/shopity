"""
URL routing configuration for the notes application.
"""

from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.note_list, name='home'),
    path('', views.note_list, name='note_list'),
    path('<int:pk>/', views.note_detail, name='note_detail'),
    path('new/', views.note_create, name='note_create'),
    path('<int:pk>/edit/', views.note_update, name='note_update'),
    path('<int:pk>/delete/', views.note_delete, name='note_delete'),
]

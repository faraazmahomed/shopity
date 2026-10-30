from django.urls import path
from . import views

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/new/", views.post_create, name="post_create"),
    path("post/<int:pk>/edit/", views.post_update, name="post_update"),
    path("authors/", views.authors_view, name="authors"),
]

app_name = "posts"

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/new/", views.post_create, name="post_create"),
    path("post/<int:pk>/edit/", views.post_update, name="post_update"),
    path("authors/", views.authors_view, name="authors"),
]

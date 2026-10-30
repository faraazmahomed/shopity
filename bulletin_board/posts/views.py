from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm
from .models import Author, Post


def post_list(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "posts/post_list.html", {"posts": posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "posts/post_detail.html", {"post": post})


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form})


def authors_view(request):
    authors = Author.objects.all()
    return render(request, "posts/authors.html", {"authors": authors})


def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_form.html", {"form": form})

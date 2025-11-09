from django.shortcuts import render
from .models import Post
from django.http import HttpRequest, HttpResponse


def post_list(request: HttpRequest) -> HttpResponse:
    """Список всех постов блога."""
    posts = Post.objects.all()
    return render(request, "blog_list.html", {"posts": posts})

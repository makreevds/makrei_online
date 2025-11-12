from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста."""
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите текст поста'}),
        }


@login_required
def post_list(request: HttpRequest) -> HttpResponse:
    """Список постов текущего пользователя."""
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "blog_list.html", {"posts": posts})


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Создание нового поста."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Пост успешно создан!')
            return redirect('blog')
    else:
        form = PostForm()
    
    return render(request, "post_form.html", {
        "form": form,
        "title": "Создать пост",
        "submit_text": "Создать"
    })


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Редактирование поста."""
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, что пост принадлежит текущему пользователю
    if post.user is None or post.user != request.user:
        return HttpResponseForbidden("Вы не можете редактировать этот пост")
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('blog')
    else:
        form = PostForm(instance=post)
    
    return render(request, "post_form.html", {
        "form": form,
        "title": "Редактировать пост",
        "submit_text": "Сохранить",
        "post": post
    })


@login_required
def post_delete(request: HttpRequest, post_id: int) -> HttpResponse:
    """Удаление поста."""
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, что пост принадлежит текущему пользователю
    if post.user is None or post.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот пост")
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален!')
        return redirect('blog')
    
    return render(request, "post_delete.html", {"post": post})

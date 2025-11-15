"""URL-маршруты для приложения passwords."""
from django.urls import path
from . import views

app_name = 'passwords'

urlpatterns = [
    path('', views.password_list, name='list'),
    path('create/', views.password_create, name='create'),
    path('<int:pk>/update/', views.password_update, name='update'),
    path('<int:pk>/delete/', views.password_delete, name='delete'),
    path('clear-session/', views.clear_session, name='clear_session'),
]


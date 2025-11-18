"""URL-маршруты для приложения hobbies."""
from django.urls import path

from . import views

app_name = 'hobbies'

urlpatterns = [
    path('', views.HobbyListView.as_view(), name='list'),
    path('create/', views.hobby_create, name='create'),
    path('<slug:slug>/', views.HobbyDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.hobby_update, name='update'),
    path('<slug:slug>/delete/', views.hobby_delete, name='delete'),
    path('<slug:slug>/entry/create/', views.entry_create, name='entry_create'),
    path('<slug:slug>/entry/<int:pk>/', views.EntryDetailView.as_view(), name='entry_detail'),
    path('<slug:slug>/entry/<int:pk>/edit/', views.entry_update, name='entry_update'),
    path('<slug:slug>/entry/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
]


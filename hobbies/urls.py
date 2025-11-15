"""URL-маршруты для приложения hobbies."""
from django.urls import path

from . import views

app_name = 'hobbies'

urlpatterns = [
    path('', views.HobbyListView.as_view(), name='list'),
    path('<slug:slug>/', views.HobbyDetailView.as_view(), name='detail'),
    path('<slug:slug>/entry/<int:pk>/', views.EntryDetailView.as_view(), name='entry_detail'),
]


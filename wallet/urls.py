"""URL-маршруты для приложения wallet."""
from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.wallet_list, name='list'),
    path('create/', views.wallet_create, name='create'),
    path('<int:wallet_id>/', views.wallet_detail, name='detail'),
    path('<int:wallet_id>/deposit/', views.wallet_deposit, name='deposit'),
    path('<int:wallet_id>/withdraw/', views.wallet_withdraw, name='withdraw'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
]


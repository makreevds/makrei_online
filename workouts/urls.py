from django.urls import path
from django.contrib.auth import views as auth_views
from .views import WelcomeView, HomeView, RegisterView, ProfileView

app_name = "workouts"

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('accounts/login/', WelcomeView.as_view(), name='login'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', HomeView.as_view(), name='home'),
    path('profile/', ProfileView.as_view(), name='profile'),
]


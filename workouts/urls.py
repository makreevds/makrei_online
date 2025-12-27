from django.urls import path
from django.contrib.auth import views as auth_views
from .views import WelcomeView, AboutView, ProgressView, RegisterView, ProfileView

app_name = "workouts"

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('accounts/login/', WelcomeView.as_view(), name='login'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', AboutView.as_view(), name='home'),
    path('progress/', ProgressView.as_view(), name='progress'),
    path('add-data/', ProfileView.as_view(), name='add-data'),
]


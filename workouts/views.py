from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
import json
from .models import WeightEntry, Workout
from .forms import WeightEntryForm, WorkoutForm


class WelcomeView(LoginView):
    """
    Приветственная страница сайта с описанием и формой входа/регистрации.
    """
    template_name = 'workouts/welcome.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Если пользователь уже авторизован, перенаправляем на /home
        if request.user.is_authenticated:
            return redirect('workouts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_form'] = UserCreationForm()
        return context


class RegisterView(View):
    """
    View для регистрации новых пользователей.
    """
    def post(self, request: HttpRequest) -> HttpResponse:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически входим после регистрации
            return redirect('workouts:home')
        # Если форма невалидна, показываем welcome страницу с формой регистрации и ошибками
        from django.contrib.auth.views import LoginView
        login_view = LoginView()
        login_view.request = request
        context = login_view.get_context_data()
        context['register_form'] = form
        context['register_errors'] = True
        return render(request, 'workouts/welcome.html', context)
    
    def get(self, request: HttpRequest) -> HttpResponse:
        # GET запросы перенаправляем на главную страницу
        return redirect('workouts:welcome')


class HomeView(LoginRequiredMixin, View):
    """
    Главная страница трекинга занятий спортом с инфографикой.
    Требует авторизации пользователя.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        # Получаем данные о весе из БД только для текущего пользователя, сортируем по дате
        weight_entries = WeightEntry.objects.filter(
            user=request.user
        ).order_by('date')
        
        # Формируем данные для графика: даты и значения веса
        weight_data = []
        for entry in weight_entries:
            weight_data.append({
                'date': entry.date.strftime('%Y-%m-%d'),
                'date_display': entry.date.strftime('%d.%m.%Y'),
                'weight': float(entry.weight_kg)
            })
        
        # Получаем количество тренировок текущего пользователя
        workouts_count = Workout.objects.filter(user=request.user).count()
        
        # Вычисляем изменение количества тренировок за текущую неделю относительно предыдущей
        now = timezone.now().date()
        
        # Начало текущей недели (понедельник)
        days_since_monday = now.weekday()
        current_week_start = now - timedelta(days=days_since_monday)
        current_week_end = current_week_start + timedelta(days=6)
        
        # Начало предыдущей недели
        previous_week_start = current_week_start - timedelta(days=7)
        previous_week_end = current_week_start - timedelta(days=1)
        
        # Количество тренировок за текущую неделю
        current_week_count = Workout.objects.filter(
            user=request.user,
            date__gte=current_week_start,
            date__lte=current_week_end
        ).count()
        
        # Количество тренировок за предыдущую неделю
        previous_week_count = Workout.objects.filter(
            user=request.user,
            date__gte=previous_week_start,
            date__lte=previous_week_end
        ).count()
        
        # Вычисляем процентное изменение
        if previous_week_count > 0:
            workouts_change_percent = round(((current_week_count - previous_week_count) / previous_week_count) * 100)
        elif current_week_count > 0:
            # Если в предыдущей неделе не было тренировок, а в текущей есть - показываем +100%
            workouts_change_percent = 100
        else:
            # Если в обеих неделях нет тренировок - показываем 0%
            workouts_change_percent = 0
        
        # Вычисляем среднюю продолжительность тренировок (только для тренировок с указанной продолжительностью)
        workouts_with_duration = Workout.objects.filter(
            user=request.user,
            duration_minutes__isnull=False
        )
        
        if workouts_with_duration.exists():
            from django.db.models import Avg
            avg_duration = workouts_with_duration.aggregate(Avg('duration_minutes'))['duration_minutes__avg']
            avg_duration = int(round(avg_duration)) if avg_duration else None
        else:
            avg_duration = None
        
        # Получаем последние тренировки для отображения
        recent_workouts = Workout.objects.filter(user=request.user).order_by('-date')[:5]
        
        # Передаем данные в контекст как JSON
        context = {
            'weight_data_json': json.dumps(weight_data, cls=DjangoJSONEncoder),
            'weight_data': weight_data,
            'user': request.user,
            'workouts_count': workouts_count,
            'workouts_change_percent': workouts_change_percent,
            'avg_duration': avg_duration,
            'recent_workouts': recent_workouts,
        }
        return render(request, 'workouts/home.html', context)


class ProfileView(LoginRequiredMixin, View):
    """
    Страница профиля пользователя с формами для добавления данных.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        """Отображение страницы профиля с формами."""
        # Очищаем сессию при отмене (если есть параметр cancel)
        if 'cancel' in request.GET and 'pending_weight_data' in request.session:
            del request.session['pending_weight_data']
        
        # Восстанавливаем форму из сессии, если есть незавершенные данные
        if 'pending_weight_data' in request.session:
            pending_data = request.session['pending_weight_data']
            from datetime import datetime
            weight_form = WeightEntryForm(initial={
                'date': pending_data.get('date'),
                'weight_kg': pending_data.get('weight_kg'),
                'notes': pending_data.get('notes', ''),
            })
        else:
            weight_form = WeightEntryForm()
        
        workout_form = WorkoutForm()
        
        context = {
            'weight_form': weight_form,
            'workout_form': workout_form,
        }
        return render(request, 'workouts/profile.html', context)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """Обработка форм добавления данных."""
        if 'add_weight' in request.POST:
            form = WeightEntryForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                # Проверяем, существует ли уже запись на эту дату
                existing_entry = WeightEntry.objects.filter(
                    user=request.user,
                    date=date
                ).first()
                
                # Если запись существует и пользователь не подтвердил обновление
                if existing_entry and 'confirm_update' not in request.POST:
                    # Сохраняем данные формы в сессии для повторного использования
                    request.session['pending_weight_data'] = {
                        'date': date.isoformat(),
                        'weight_kg': str(form.cleaned_data['weight_kg']),
                        'notes': form.cleaned_data.get('notes', ''),
                    }
                    workout_form = WorkoutForm()
                    context = {
                        'weight_form': form,
                        'workout_form': workout_form,
                        'existing_weight_entry': existing_entry,
                        'show_update_modal': True,
                    }
                    return render(request, 'workouts/profile.html', context)
                
                # Если пользователь подтвердил обновление или записи нет
                if existing_entry and 'confirm_update' in request.POST:
                    # Обновляем существующую запись
                    weight_entry = existing_entry
                else:
                    # Создаем новую запись
                    weight_entry = WeightEntry(user=request.user)
                
                weight_entry.date = date
                weight_entry.weight_kg = form.cleaned_data['weight_kg']
                weight_entry.notes = form.cleaned_data.get('notes', '')
                weight_entry.save()
                
                # Очищаем данные из сессии
                if 'pending_weight_data' in request.session:
                    del request.session['pending_weight_data']
                
                messages.success(request, 'Вес успешно сохранен!')
                return redirect('workouts:profile')
            else:
                workout_form = WorkoutForm()
                context = {
                    'weight_form': form,
                    'workout_form': workout_form,
                }
                return render(request, 'workouts/profile.html', context)
        
        elif 'add_workout' in request.POST:
            form = WorkoutForm(request.POST)
            if form.is_valid():
                workout = form.save(commit=False)
                workout.user = request.user
                workout.save()
                messages.success(request, 'Тренировка успешно добавлена!')
                return redirect('workouts:profile')
            else:
                weight_form = WeightEntryForm()
                context = {
                    'weight_form': weight_form,
                    'workout_form': form,
                }
                return render(request, 'workouts/profile.html', context)
        
        return redirect('workouts:profile')

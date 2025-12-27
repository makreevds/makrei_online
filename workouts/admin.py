from django.contrib import admin
from .models import WeightEntry, Workout


@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight_kg', 'created_at']
    list_filter = ['user', 'date', 'created_at']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'date', 'weight_kg')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Фильтруем записи: обычные пользователи видят только свои, суперпользователи - все"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        """Устанавливаем пользователя при создании записи"""
        if not change:  # Если это новая запись
            # Проверяем, что было выбрано в форме
            if form.cleaned_data and 'user' in form.cleaned_data:
                selected_user = form.cleaned_data['user']
                if selected_user and request.user.is_superuser:
                    # Суперпользователь выбрал пользователя - используем его
                    obj.user = selected_user
                elif not request.user.is_superuser:
                    # Обычный пользователь - всегда устанавливаем себя
                    obj.user = request.user
                elif not selected_user:
                    # Пользователь не выбран - устанавливаем текущего
                    obj.user = request.user
            else:
                # Если данных формы нет - устанавливаем текущего пользователя
                obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """Проверяем права на изменение: можно изменять только свои записи"""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Проверяем права на удаление: можно удалять только свои записи"""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_delete_permission(request, obj)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'workout_type', 'duration_minutes', 'created_at']
    list_filter = ['user', 'date', 'workout_type', 'created_at']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'date', 'workout_type', 'duration_minutes')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Фильтруем записи: обычные пользователи видят только свои, суперпользователи - все"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        """Устанавливаем пользователя при создании записи"""
        if not change:  # Если это новая запись
            # Проверяем, что было выбрано в форме
            if form.cleaned_data and 'user' in form.cleaned_data:
                selected_user = form.cleaned_data['user']
                if selected_user and request.user.is_superuser:
                    # Суперпользователь выбрал пользователя - используем его
                    obj.user = selected_user
                elif not request.user.is_superuser:
                    # Обычный пользователь - всегда устанавливаем себя
                    obj.user = request.user
                elif not selected_user:
                    # Пользователь не выбран - устанавливаем текущего
                    obj.user = request.user
            else:
                # Если данных формы нет - устанавливаем текущего пользователя
                obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """Проверяем права на изменение: можно изменять только свои записи"""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Проверяем права на удаление: можно удалять только свои записи"""
        if obj is not None and not request.user.is_superuser:
            return obj.user == request.user
        return super().has_delete_permission(request, obj)

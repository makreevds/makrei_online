# Generated migration to populate user field for existing WeightEntry records

from django.db import migrations
from django.contrib.auth import get_user_model

User = get_user_model()


def populate_user_field(apps, schema_editor):
    """Заполняем поле user для существующих записей веса"""
    WeightEntry = apps.get_model('workouts', 'WeightEntry')
    
    # Получаем первого суперпользователя или создаем дефолтного
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        
        if user:
            # Привязываем все записи без пользователя к этому пользователю
            WeightEntry.objects.filter(user__isnull=True).update(user=user)
    except Exception:
        # Если что-то пошло не так, просто пропускаем
        pass


def reverse_populate_user_field(apps, schema_editor):
    """Обратная операция - очищаем поле user"""
    WeightEntry = apps.get_model('workouts', 'WeightEntry')
    WeightEntry.objects.all().update(user=None)


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0005_alter_weightentry_unique_together_weightentry_user_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_user_field, reverse_populate_user_field),
    ]


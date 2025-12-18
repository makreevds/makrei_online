# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cryptocurrency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Полное название криптовалюты (например, Bitcoin)', max_length=100, verbose_name='Название')),
                ('symbol', models.CharField(db_index=True, help_text='Символ криптовалюты (например, BTC)', max_length=10, unique=True, verbose_name='Символ')),
                ('network', models.CharField(help_text='Название сети блокчейна', max_length=50, verbose_name='Сеть')),
                ('decimals', models.PositiveSmallIntegerField(default=8, help_text='Точность отображения суммы', verbose_name='Количество знаков после запятой')),
                ('is_active', models.BooleanField(default=True, help_text='Доступна ли криптовалюта для использования', verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
            ],
            options={
                'verbose_name': 'Криптовалюта',
                'verbose_name_plural': 'Криптовалюты',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, help_text='Публичный адрес кошелька', max_length=255, unique=True, verbose_name='Адрес кошелька')),
                ('private_key_encrypted', models.TextField(blank=True, help_text='Приватный ключ в зашифрованном виде', null=True, verbose_name='Приватный ключ (зашифрован)')),
                ('balance', models.DecimalField(decimal_places=8, default=Decimal('0.0'), help_text='Текущий баланс кошелька', max_digits=20, validators=[MinValueValidator(Decimal('0.0'))], verbose_name='Баланс')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('cryptocurrency', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.PROTECT, related_name='wallets', to='wallet.cryptocurrency', verbose_name='Криптовалюта')),
                ('user', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='wallets', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Кошелёк',
                'verbose_name_plural': 'Кошельки',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'cryptocurrency')},
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('deposit', 'Пополнение'), ('withdrawal', 'Вывод'), ('transfer', 'Перевод')], db_index=True, max_length=20, verbose_name='Тип транзакции')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('confirmed', 'Подтверждена'), ('failed', 'Ошибка'), ('cancelled', 'Отменена')], db_index=True, default='pending', max_length=20, verbose_name='Статус')),
                ('amount', models.DecimalField(decimal_places=8, help_text='Сумма транзакции', max_digits=20, validators=[MinValueValidator(Decimal('0.00000001'))], verbose_name='Сумма')),
                ('fee', models.DecimalField(decimal_places=8, default=Decimal('0.0'), help_text='Комиссия сети', max_digits=20, validators=[MinValueValidator(Decimal('0.0'))], verbose_name='Комиссия')),
                ('from_address', models.CharField(blank=True, help_text='Адрес, с которого отправлены средства', max_length=255, null=True, verbose_name='Адрес отправителя')),
                ('to_address', models.CharField(help_text='Адрес, на который отправлены средства', max_length=255, verbose_name='Адрес получателя')),
                ('tx_hash', models.CharField(blank=True, db_index=True, help_text='Хеш транзакции в блокчейне', max_length=255, null=True, unique=True, verbose_name='Хеш транзакции')),
                ('block_number', models.BigIntegerField(blank=True, help_text='Номер блока, в котором подтверждена транзакция', null=True, verbose_name='Номер блока')),
                ('confirmations', models.PositiveIntegerField(default=0, help_text='Количество подтверждений транзакции', verbose_name='Подтверждения')),
                ('description', models.TextField(blank=True, help_text='Дополнительная информация о транзакции', verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('confirmed_at', models.DateTimeField(blank=True, help_text='Время подтверждения транзакции', null=True, verbose_name='Подтверждено')),
                ('wallet', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='wallet.wallet', verbose_name='Кошелёк')),
            ],
            options={
                'verbose_name': 'Транзакция',
                'verbose_name_plural': 'Транзакции',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='cryptocurrency',
            index=models.Index(fields=['symbol', 'is_active'], name='wallet_cryp_symbol__idx'),
        ),
        migrations.AddIndex(
            model_name='wallet',
            index=models.Index(fields=['user', 'cryptocurrency'], name='wallet_wall_user_id__idx'),
        ),
        migrations.AddIndex(
            model_name='wallet',
            index=models.Index(fields=['address'], name='wallet_wall_address_idx'),
        ),
        migrations.AddIndex(
            model_name='wallet',
            index=models.Index(fields=['-created_at'], name='wallet_wall_created__idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['wallet', '-created_at'], name='wallet_tran_wallet__idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_type', 'status'], name='wallet_tran_transac__idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['tx_hash'], name='wallet_tran_tx_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['-created_at'], name='wallet_tran_created__idx'),
        ),
    ]


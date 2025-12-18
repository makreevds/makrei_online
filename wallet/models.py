"""Модели для управления криптовалютными кошельками."""
from typing import Optional
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


class Cryptocurrency(models.Model):
    """
    Модель для хранения информации о поддерживаемых криптовалютах.
    
    Содержит базовую информацию о криптовалюте: название, символ,
    сеть блокчейна и другие параметры.
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
        help_text='Полное название криптовалюты (например, Bitcoin)'
    )
    symbol = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Символ',
        help_text='Символ криптовалюты (например, BTC)',
        db_index=True
    )
    network = models.CharField(
        max_length=50,
        verbose_name='Сеть',
        help_text='Название сети блокчейна'
    )
    decimals = models.PositiveSmallIntegerField(
        default=8,
        verbose_name='Количество знаков после запятой',
        help_text='Точность отображения суммы'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Доступна ли криптовалюта для использования'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    
    class Meta:
        verbose_name = 'Криптовалюта'
        verbose_name_plural = 'Криптовалюты'
        ordering = ['name']
        indexes = [
            models.Index(fields=['symbol', 'is_active']),
        ]
    
    def __str__(self) -> str:
        """Строковое представление криптовалюты."""
        return f"{self.name} ({self.symbol})"


class Wallet(models.Model):
    """
    Модель криптовалютного кошелька пользователя.
    
    Каждый пользователь может иметь несколько кошельков для разных
    криптовалют. Кошелёк хранит адрес и баланс.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallets',
        verbose_name='Пользователь',
        db_index=True
    )
    cryptocurrency = models.ForeignKey(
        Cryptocurrency,
        on_delete=models.PROTECT,
        related_name='wallets',
        verbose_name='Криптовалюта',
        db_index=True
    )
    address = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Адрес кошелька',
        help_text='Публичный адрес кошелька',
        db_index=True
    )
    private_key_encrypted = models.TextField(
        verbose_name='Приватный ключ (зашифрован)',
        help_text='Приватный ключ в зашифрованном виде',
        blank=True,
        null=True
    )
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
        verbose_name='Баланс',
        help_text='Текущий баланс кошелька'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    
    class Meta:
        verbose_name = 'Кошелёк'
        verbose_name_plural = 'Кошельки'
        ordering = ['-created_at']
        unique_together = [['user', 'cryptocurrency']]
        indexes = [
            models.Index(fields=['user', 'cryptocurrency']),
            models.Index(fields=['address']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self) -> str:
        """Строковое представление кошелька."""
        return f"{self.user.username} - {self.cryptocurrency.symbol} ({self.address[:10]}...)"
    
    @property
    def display_balance(self) -> str:
        """Возвращает баланс в читаемом формате."""
        return f"{self.balance:.{self.cryptocurrency.decimals}f} {self.cryptocurrency.symbol}"


class Transaction(models.Model):
    """
    Модель транзакции криптовалюты.
    
    Хранит информацию о всех операциях: пополнение, вывод, переводы.
    """
    
    class TransactionType(models.TextChoices):
        """Типы транзакций."""
        DEPOSIT = 'deposit', 'Пополнение'
        WITHDRAWAL = 'withdrawal', 'Вывод'
        TRANSFER = 'transfer', 'Перевод'
    
    class TransactionStatus(models.TextChoices):
        """Статусы транзакций."""
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждена'
        FAILED = 'failed', 'Ошибка'
        CANCELLED = 'cancelled', 'Отменена'
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Кошелёк',
        db_index=True
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name='Тип транзакции',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        verbose_name='Статус',
        db_index=True
    )
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))],
        verbose_name='Сумма',
        help_text='Сумма транзакции'
    )
    fee = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
        verbose_name='Комиссия',
        help_text='Комиссия сети'
    )
    from_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Адрес отправителя',
        help_text='Адрес, с которого отправлены средства'
    )
    to_address = models.CharField(
        max_length=255,
        verbose_name='Адрес получателя',
        help_text='Адрес, на который отправлены средства'
    )
    tx_hash = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Хеш транзакции',
        help_text='Хеш транзакции в блокчейне',
        db_index=True
    )
    block_number = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name='Номер блока',
        help_text='Номер блока, в котором подтверждена транзакция'
    )
    confirmations = models.PositiveIntegerField(
        default=0,
        verbose_name='Подтверждения',
        help_text='Количество подтверждений транзакции'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
        help_text='Дополнительная информация о транзакции'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Подтверждено',
        help_text='Время подтверждения транзакции'
    )
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', '-created_at']),
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['tx_hash']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self) -> str:
        """Строковое представление транзакции."""
        return (
            f"{self.get_transaction_type_display()} - "
            f"{self.amount} {self.wallet.cryptocurrency.symbol} - "
            f"{self.get_status_display()}"
        )
    
    def confirm(self) -> None:
        """Подтверждает транзакцию."""
        self.status = self.TransactionStatus.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at', 'updated_at'])
    
    def fail(self) -> None:
        """Помечает транзакцию как неудачную."""
        self.status = self.TransactionStatus.FAILED
        self.save(update_fields=['status', 'updated_at'])

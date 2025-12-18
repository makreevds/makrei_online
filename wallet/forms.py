"""Формы для работы с криптовалютными кошельками."""
from typing import Optional
from decimal import Decimal
from django import forms
from django.core.validators import MinValueValidator
from .models import Wallet, Transaction, Cryptocurrency


class WalletCreateForm(forms.ModelForm):
    """Форма для создания нового кошелька."""
    
    cryptocurrency = forms.ModelChoiceField(
        queryset=Cryptocurrency.objects.filter(is_active=True),
        label='Криптовалюта',
        help_text='Выберите криптовалюту для кошелька',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Wallet
        fields = ['cryptocurrency']
    
    def __init__(self, *args, user=None, **kwargs):
        """
        Инициализация формы.
        
        Args:
            user: Пользователь, для которого создаётся кошелёк
        """
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean(self) -> dict:
        """
        Проверяет, что у пользователя ещё нет кошелька для выбранной криптовалюты.
        
        Returns:
            Очищенные данные формы
        """
        cleaned_data = super().clean()
        cryptocurrency = cleaned_data.get('cryptocurrency')
        
        if cryptocurrency and self.user:
            if Wallet.objects.filter(
                user=self.user,
                cryptocurrency=cryptocurrency
            ).exists():
                raise forms.ValidationError(
                    f"У вас уже есть кошелёк для {cryptocurrency.name}"
                )
        
        return cleaned_data


class DepositForm(forms.Form):
    """Форма для пополнения кошелька."""
    
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        min_value=Decimal('0.00000001'),
        label='Сумма пополнения',
        help_text='Введите сумму для пополнения',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.00000001',
            'placeholder': '0.00000000'
        })
    )
    description = forms.CharField(
        required=False,
        max_length=500,
        label='Описание',
        help_text='Дополнительная информация о пополнении',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Необязательное описание'
        })
    )
    
    def __init__(self, *args, wallet=None, **kwargs):
        """
        Инициализация формы.
        
        Args:
            wallet: Кошелёк, который пополняется
        """
        super().__init__(*args, **kwargs)
        self.wallet = wallet
        if wallet:
            # Устанавливаем подсказку с символом криптовалюты
            self.fields['amount'].help_text = (
                f"Введите сумму в {wallet.cryptocurrency.symbol}"
            )


class WithdrawalForm(forms.Form):
    """Форма для вывода средств с кошелька."""
    
    to_address = forms.CharField(
        max_length=255,
        label='Адрес получателя',
        help_text='Введите адрес кошелька, на который хотите вывести средства',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес кошелька'
        })
    )
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        min_value=Decimal('0.00000001'),
        label='Сумма вывода',
        help_text='Введите сумму для вывода',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.00000001',
            'placeholder': '0.00000000'
        })
    )
    fee = forms.DecimalField(
        max_digits=20,
        decimal_places=8,
        min_value=Decimal('0.0'),
        required=False,
        label='Комиссия сети',
        help_text='Комиссия за транзакцию (оставьте пустым для автоматического расчёта)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.00000001',
            'placeholder': 'Автоматически'
        })
    )
    description = forms.CharField(
        required=False,
        max_length=500,
        label='Описание',
        help_text='Дополнительная информация о выводе',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Необязательное описание'
        })
    )
    
    def __init__(self, *args, wallet=None, **kwargs):
        """
        Инициализация формы.
        
        Args:
            wallet: Кошелёк, с которого выводятся средства
        """
        super().__init__(*args, **kwargs)
        self.wallet = wallet
    
    def clean_amount(self) -> Decimal:
        """
        Проверяет, что сумма не превышает баланс кошелька.
        
        Returns:
            Очищенная сумма
        """
        amount = self.cleaned_data.get('amount')
        
        if amount and self.wallet:
            if amount > self.wallet.balance:
                raise forms.ValidationError(
                    f"Недостаточно средств. Доступно: "
                    f"{self.wallet.display_balance}"
                )
        
        return amount
    
    def clean_to_address(self) -> str:
        """
        Проверяет формат адреса получателя.
        
        Returns:
            Очищенный адрес
        """
        address = self.cleaned_data.get('to_address')
        
        if address and self.wallet:
            # Базовая проверка формата адреса
            crypto = self.wallet.cryptocurrency.symbol
            
            if crypto == 'BTC':
                # Bitcoin адреса обычно начинаются с 1, 3, или bc1
                if not (address.startswith('1') or 
                        address.startswith('3') or 
                        address.startswith('bc1')):
                    raise forms.ValidationError(
                        "Неверный формат Bitcoin адреса"
                    )
            elif crypto == 'ETH':
                # Ethereum адреса начинаются с 0x и имеют длину 42 символа
                if not (address.startswith('0x') and len(address) == 42):
                    raise forms.ValidationError(
                        "Неверный формат Ethereum адреса"
                    )
        
        return address


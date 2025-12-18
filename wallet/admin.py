"""Административный интерфейс для управления кошельками."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Cryptocurrency, Wallet, Transaction


@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    """Административный интерфейс для криптовалют."""
    
    list_display = ['name', 'symbol', 'network', 'decimals', 'is_active', 'created_at']
    list_filter = ['is_active', 'network', 'created_at']
    search_fields = ['name', 'symbol', 'network']
    readonly_fields = ['created_at']
    list_editable = ['is_active']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Административный интерфейс для кошельков."""
    
    list_display = [
        'user', 'cryptocurrency', 'address_short', 'balance_display', 
        'created_at', 'updated_at'
    ]
    list_filter = ['cryptocurrency', 'created_at']
    search_fields = ['user__username', 'address', 'cryptocurrency__symbol']
    readonly_fields = ['created_at', 'updated_at', 'balance']
    raw_id_fields = ['user']
    
    def address_short(self, obj: Wallet) -> str:
        """Короткое представление адреса."""
        if len(obj.address) > 20:
            return f"{obj.address[:10]}...{obj.address[-10:]}"
        return obj.address
    address_short.short_description = 'Адрес'
    
    def balance_display(self, obj: Wallet) -> str:
        """Отображение баланса."""
        return obj.display_balance
    balance_display.short_description = 'Баланс'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Административный интерфейс для транзакций."""
    
    list_display = [
        'id', 'wallet', 'transaction_type', 'status', 'amount_display',
        'tx_hash_short', 'confirmations', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at', 'wallet__cryptocurrency']
    search_fields = ['tx_hash', 'from_address', 'to_address', 'wallet__user__username']
    readonly_fields = [
        'created_at', 'updated_at', 'confirmed_at', 'tx_hash', 
        'block_number', 'confirmations'
    ]
    raw_id_fields = ['wallet']
    date_hierarchy = 'created_at'
    
    def amount_display(self, obj: Transaction) -> str:
        """Отображение суммы транзакции."""
        return f"{obj.amount} {obj.wallet.cryptocurrency.symbol}"
    amount_display.short_description = 'Сумма'
    
    def tx_hash_short(self, obj: Transaction) -> str:
        """Короткое представление хеша транзакции."""
        if obj.tx_hash and len(obj.tx_hash) > 20:
            return f"{obj.tx_hash[:10]}...{obj.tx_hash[-10:]}"
        return obj.tx_hash or '-'
    tx_hash_short.short_description = 'Хеш транзакции'
    
    def cryptocurrency(self, obj: Transaction) -> str:
        """Криптовалюта транзакции."""
        return obj.wallet.cryptocurrency.symbol
    cryptocurrency.short_description = 'Криптовалюта'

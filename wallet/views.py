"""Представления для работы с криптовалютными кошельками."""
from typing import Optional
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Wallet, Transaction, Cryptocurrency
from .forms import WalletCreateForm, DepositForm, WithdrawalForm
from .services import BlockchainServiceFactory


@login_required
def wallet_list(request):
    """
    Отображает список кошельков пользователя.
    
    Returns:
        HTTP ответ с шаблоном списка кошельков
    """
    wallets = Wallet.objects.filter(user=request.user).select_related(
        'cryptocurrency'
    ).order_by('-created_at')
    
    context = {
        'wallets': wallets,
        'available_cryptocurrencies': Cryptocurrency.objects.filter(
            is_active=True
        )
    }
    
    return render(request, 'wallet/wallet_list.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def wallet_create(request):
    """
    Создаёт новый кошелёк для пользователя.
    
    Returns:
        HTTP ответ с формой создания или редирект на список кошельков
    """
    if request.method == 'POST':
        form = WalletCreateForm(request.POST, user=request.user)
        
        if form.is_valid():
            cryptocurrency = form.cleaned_data['cryptocurrency']
            
            try:
                # Проверяем, нет ли уже кошелька для этой криптовалюты
                existing_wallet = Wallet.objects.filter(
                    user=request.user,
                    cryptocurrency=cryptocurrency
                ).first()
                
                if existing_wallet:
                    messages.error(
                        request,
                        f"У вас уже есть кошелёк для {cryptocurrency.name}"
                    )
                    return redirect('wallet:list')
                
                # Получаем сервис блокчейна
                blockchain_service = BlockchainServiceFactory.get_service(
                    cryptocurrency.symbol
                )
                
                # Генерируем новый кошелёк
                wallet_data = blockchain_service.generate_wallet()
                
                # Создаём кошелёк в базе данных
                with db_transaction.atomic():
                    wallet = Wallet.objects.create(
                        user=request.user,
                        cryptocurrency=cryptocurrency,
                        address=wallet_data['address'],
                        private_key_encrypted=blockchain_service.encrypt_private_key(
                            wallet_data['private_key']
                        ),
                        balance=Decimal('0.0')
                    )
                
                messages.success(
                    request,
                    f"Кошелёк {cryptocurrency.name} успешно создан!"
                )
                return redirect('wallet:detail', wallet_id=wallet.id)
            
            except Exception as e:
                messages.error(
                    request,
                    f"Ошибка при создании кошелька: {str(e)}"
                )
    else:
        form = WalletCreateForm(user=request.user)
    
    context = {
        'form': form,
        'available_cryptocurrencies': Cryptocurrency.objects.filter(
            is_active=True
        )
    }
    
    return render(request, 'wallet/wallet_create.html', context)


@login_required
def wallet_detail(request, wallet_id: int):
    """
    Отображает детальную информацию о кошельке.
    
    Args:
        wallet_id: ID кошелька
        
    Returns:
        HTTP ответ с детальной информацией о кошельке
    """
    wallet = get_object_or_404(
        Wallet,
        id=wallet_id,
        user=request.user
    )
    
    # Получаем последние транзакции
    transactions = Transaction.objects.filter(
        wallet=wallet
    ).order_by('-created_at')[:20]
    
    # Обновляем баланс из блокчейна (если не тестовый режим)
    try:
        blockchain_service = BlockchainServiceFactory.get_service(
            wallet.cryptocurrency.symbol
        )
        # В тестовом режиме не обновляем баланс автоматически
        # В продакшене можно добавить обновление баланса
    except Exception:
        pass
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    
    return render(request, 'wallet/wallet_detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def wallet_deposit(request, wallet_id: int):
    """
    Пополнение кошелька.
    
    Args:
        wallet_id: ID кошелька
        
    Returns:
        HTTP ответ с формой пополнения или редирект
    """
    wallet = get_object_or_404(
        Wallet,
        id=wallet_id,
        user=request.user
    )
    
    if request.method == 'POST':
        form = DepositForm(request.POST, wallet=wallet)
        
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            
            try:
                with db_transaction.atomic():
                    # Создаём транзакцию пополнения
                    transaction = Transaction.objects.create(
                        wallet=wallet,
                        transaction_type=Transaction.TransactionType.DEPOSIT,
                        status=Transaction.TransactionStatus.PENDING,
                        amount=amount,
                        to_address=wallet.address,
                        description=description
                    )
                    
                    # Обновляем баланс кошелька
                    wallet.balance += amount
                    wallet.save(update_fields=['balance', 'updated_at'])
                    
                    # Подтверждаем транзакцию (в реальной системе это делается
                    # после подтверждения в блокчейне)
                    transaction.confirm()
                
                messages.success(
                    request,
                    f"Кошелёк пополнен на {amount} {wallet.cryptocurrency.symbol}"
                )
                return redirect('wallet:detail', wallet_id=wallet.id)
            
            except Exception as e:
                messages.error(
                    request,
                    f"Ошибка при пополнении кошелька: {str(e)}"
                )
    else:
        form = DepositForm(wallet=wallet)
    
    context = {
        'form': form,
        'wallet': wallet,
    }
    
    return render(request, 'wallet/wallet_deposit.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def wallet_withdraw(request, wallet_id: int):
    """
    Вывод средств с кошелька.
    
    Args:
        wallet_id: ID кошелька
        
    Returns:
        HTTP ответ с формой вывода или редирект
    """
    wallet = get_object_or_404(
        Wallet,
        id=wallet_id,
        user=request.user
    )
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, wallet=wallet)
        
        if form.is_valid():
            to_address = form.cleaned_data['to_address']
            amount = form.cleaned_data['amount']
            fee = form.cleaned_data.get('fee') or Decimal('0.0')
            description = form.cleaned_data.get('description', '')
            
            # Проверяем баланс с учётом комиссии
            total_amount = amount + fee
            if total_amount > wallet.balance:
                messages.error(
                    request,
                    f"Недостаточно средств. "
                    f"Требуется: {total_amount} {wallet.cryptocurrency.symbol}, "
                    f"доступно: {wallet.balance} {wallet.cryptocurrency.symbol}"
                )
                form = WithdrawalForm(request.POST, wallet=wallet)
                context = {'form': form, 'wallet': wallet}
                return render(request, 'wallet/wallet_withdraw.html', context)
            
            try:
                # Получаем сервис блокчейна
                blockchain_service = BlockchainServiceFactory.get_service(
                    wallet.cryptocurrency.symbol
                )
                
                # Расшифровываем приватный ключ
                private_key = blockchain_service.decrypt_private_key(
                    wallet.private_key_encrypted
                )
                
                # Создаём транзакцию в блокчейне
                tx_data = blockchain_service.create_transaction(
                    from_address=wallet.address,
                    to_address=to_address,
                    amount=amount,
                    private_key=private_key,
                    fee=fee
                )
                
                with db_transaction.atomic():
                    # Создаём запись о транзакции
                    transaction = Transaction.objects.create(
                        wallet=wallet,
                        transaction_type=Transaction.TransactionType.WITHDRAWAL,
                        status=Transaction.TransactionStatus.PENDING,
                        amount=amount,
                        fee=fee,
                        from_address=wallet.address,
                        to_address=to_address,
                        tx_hash=tx_data.get('tx_hash'),
                        description=description
                    )
                    
                    # Обновляем баланс кошелька
                    wallet.balance -= total_amount
                    wallet.save(update_fields=['balance', 'updated_at'])
                
                messages.success(
                    request,
                    f"Транзакция создана. Хеш: {tx_data.get('tx_hash', 'N/A')}"
                )
                return redirect('wallet:detail', wallet_id=wallet.id)
            
            except Exception as e:
                messages.error(
                    request,
                    f"Ошибка при выводе средств: {str(e)}"
                )
    else:
        form = WithdrawalForm(wallet=wallet)
    
    context = {
        'form': form,
        'wallet': wallet,
    }
    
    return render(request, 'wallet/wallet_withdraw.html', context)


@login_required
def transaction_list(request):
    """
    Отображает список всех транзакций пользователя.
    
    Returns:
        HTTP ответ с списком транзакций
    """
    transactions = Transaction.objects.filter(
        wallet__user=request.user
    ).select_related(
        'wallet',
        'wallet__cryptocurrency'
    ).order_by('-created_at')
    
    context = {
        'transactions': transactions,
    }
    
    return render(request, 'wallet/transaction_list.html', context)


@login_required
def transaction_detail(request, transaction_id: int):
    """
    Отображает детальную информацию о транзакции.
    
    Args:
        transaction_id: ID транзакции
        
    Returns:
        HTTP ответ с детальной информацией о транзакции
    """
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        wallet__user=request.user
    )
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'wallet/transaction_detail.html', context)

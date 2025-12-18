"""Сервисы для работы с криптовалютными блокчейнами."""
from typing import Optional, Dict, Any
from decimal import Decimal
from abc import ABC, abstractmethod
from django.conf import settings
from cryptography.fernet import Fernet
import hashlib
import secrets


class BlockchainService(ABC):
    """Абстрактный базовый класс для работы с блокчейном."""
    
    def __init__(self, cryptocurrency_symbol: str):
        """
        Инициализация сервиса блокчейна.
        
        Args:
            cryptocurrency_symbol: Символ криптовалюты (BTC, ETH и т.д.)
        """
        self.cryptocurrency_symbol = cryptocurrency_symbol
        self._encryption_key = self._get_encryption_key()
    
    def _get_encryption_key(self) -> bytes:
        """
        Получает ключ шифрования из настроек.
        
        Returns:
            Ключ шифрования в виде bytes
        """
        # В продакшене ключ должен храниться в переменных окружения
        key = getattr(settings, 'WALLET_ENCRYPTION_KEY', None)
        if not key:
            # Генерируем ключ на основе SECRET_KEY для разработки
            secret_key = settings.SECRET_KEY.encode()
            key = hashlib.sha256(secret_key).digest()
            # Fernet требует 32 байта, base64-encoded
            from base64 import urlsafe_b64encode
            key = urlsafe_b64encode(key)
        else:
            if isinstance(key, str):
                key = key.encode()
        return key
    
    def encrypt_private_key(self, private_key: str) -> str:
        """
        Шифрует приватный ключ.
        
        Args:
            private_key: Приватный ключ в виде строки
            
        Returns:
            Зашифрованный приватный ключ
        """
        fernet = Fernet(self._encryption_key)
        encrypted = fernet.encrypt(private_key.encode())
        return encrypted.decode()
    
    def decrypt_private_key(self, encrypted_key: str) -> str:
        """
        Расшифровывает приватный ключ.
        
        Args:
            encrypted_key: Зашифрованный приватный ключ
            
        Returns:
            Расшифрованный приватный ключ
        """
        fernet = Fernet(self._encryption_key)
        decrypted = fernet.decrypt(encrypted_key.encode())
        return decrypted.decode()
    
    @abstractmethod
    def generate_wallet(self) -> Dict[str, str]:
        """
        Генерирует новый кошелёк.
        
        Returns:
            Словарь с адресом и приватным ключом
        """
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> Decimal:
        """
        Получает баланс кошелька.
        
        Args:
            address: Адрес кошелька
            
        Returns:
            Баланс в Decimal
        """
        pass
    
    @abstractmethod
    def create_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal,
        private_key: str,
        fee: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Создаёт транзакцию в блокчейне.
        
        Args:
            from_address: Адрес отправителя
            to_address: Адрес получателя
            amount: Сумма перевода
            private_key: Приватный ключ отправителя
            fee: Комиссия (опционально)
            
        Returns:
            Словарь с информацией о транзакции (tx_hash и т.д.)
        """
        pass
    
    @abstractmethod
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Получает статус транзакции.
        
        Args:
            tx_hash: Хеш транзакции
            
        Returns:
            Словарь с информацией о статусе транзакции
        """
        pass


class BitcoinService(BlockchainService):
    """Сервис для работы с Bitcoin."""
    
    def __init__(self):
        """Инициализация сервиса Bitcoin."""
        super().__init__('BTC')
        # В продакшене здесь будет подключение к Bitcoin RPC или API
        self._test_mode = getattr(settings, 'WALLET_TEST_MODE', True)
    
    def generate_wallet(self) -> Dict[str, str]:
        """
        Генерирует новый Bitcoin кошелёк.
        
        В тестовом режиме генерирует случайные данные.
        В продакшене использует библиотеку bitcoinlib или аналогичную.
        """
        if self._test_mode:
            # Тестовый режим: генерируем случайные данные
            address = 'bc1' + secrets.token_hex(20)
            private_key = secrets.token_hex(32)
            return {
                'address': address,
                'private_key': private_key
            }
        else:
            # Продакшен: используем реальную библиотеку
            # try:
            #     from bitcoinlib.wallets import Wallet
            #     wallet = Wallet.create('temp_wallet')
            #     return {
            #         'address': wallet.get_key().address,
            #         'private_key': wallet.get_key().wif
            #     }
            # except ImportError:
            #     raise ImportError(
            #         "Для работы с Bitcoin установите библиотеку bitcoinlib: "
            #         "pip install bitcoinlib"
            #     )
            raise NotImplementedError(
                "Реальная генерация Bitcoin кошельков требует установки "
                "библиотеки bitcoinlib и настройки подключения к Bitcoin сети"
            )
    
    def get_balance(self, address: str) -> Decimal:
        """
        Получает баланс Bitcoin кошелька.
        
        В тестовом режиме возвращает случайный баланс.
        В продакшене использует API блокчейна.
        """
        if self._test_mode:
            # Тестовый режим: возвращаем случайный баланс
            import random
            return Decimal(str(random.uniform(0, 10)))
        else:
            # Продакшен: используем API блокчейна
            # Например, через blockchain.info API или собственный RPC
            raise NotImplementedError(
                "Получение реального баланса требует настройки "
                "подключения к Bitcoin API"
            )
    
    def create_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal,
        private_key: str,
        fee: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Создаёт Bitcoin транзакцию.
        
        В тестовом режиме возвращает тестовые данные.
        """
        if self._test_mode:
            # Тестовый режим: генерируем тестовый хеш
            tx_hash = '0x' + secrets.token_hex(32)
            return {
                'tx_hash': tx_hash,
                'status': 'pending',
                'fee': fee or Decimal('0.00001')
            }
        else:
            raise NotImplementedError(
                "Создание реальных транзакций требует настройки "
                "Bitcoin RPC или использования библиотеки bitcoinlib"
            )
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Получает статус Bitcoin транзакции.
        
        В тестовом режиме возвращает тестовые данные.
        """
        if self._test_mode:
            return {
                'status': 'confirmed',
                'confirmations': 6,
                'block_number': 123456
            }
        else:
            raise NotImplementedError(
                "Получение статуса транзакций требует настройки "
                "подключения к Bitcoin API"
            )


class EthereumService(BlockchainService):
    """Сервис для работы с Ethereum."""
    
    def __init__(self):
        """Инициализация сервиса Ethereum."""
        super().__init__('ETH')
        self._test_mode = getattr(settings, 'WALLET_TEST_MODE', True)
    
    def generate_wallet(self) -> Dict[str, str]:
        """
        Генерирует новый Ethereum кошелёк.
        
        В тестовом режиме генерирует случайные данные.
        В продакшене использует библиотеку web3.py.
        """
        if self._test_mode:
            # Тестовый режим: генерируем случайные данные
            address = '0x' + secrets.token_hex(20)
            private_key = '0x' + secrets.token_hex(32)
            return {
                'address': address,
                'private_key': private_key
            }
        else:
            # Продакшен: используем web3.py
            # try:
            #     from eth_account import Account
            #     account = Account.create()
            #     return {
            #         'address': account.address,
            #         'private_key': account.key.hex()
            #     }
            # except ImportError:
            #     raise ImportError(
            #         "Для работы с Ethereum установите библиотеку web3: "
            #         "pip install web3 eth-account"
            #     )
            raise NotImplementedError(
                "Реальная генерация Ethereum кошельков требует установки "
                "библиотеки web3 и eth-account"
            )
    
    def get_balance(self, address: str) -> Decimal:
        """
        Получает баланс Ethereum кошелька.
        
        В тестовом режиме возвращает случайный баланс.
        """
        if self._test_mode:
            import random
            return Decimal(str(random.uniform(0, 10)))
        else:
            raise NotImplementedError(
                "Получение реального баланса требует настройки "
                "подключения к Ethereum RPC"
            )
    
    def create_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal,
        private_key: str,
        fee: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Создаёт Ethereum транзакцию.
        
        В тестовом режиме возвращает тестовые данные.
        """
        if self._test_mode:
            tx_hash = '0x' + secrets.token_hex(32)
            return {
                'tx_hash': tx_hash,
                'status': 'pending',
                'fee': fee or Decimal('0.0001')
            }
        else:
            raise NotImplementedError(
                "Создание реальных транзакций требует настройки "
                "Ethereum RPC и использования web3.py"
            )
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Получает статус Ethereum транзакции.
        
        В тестовом режиме возвращает тестовые данные.
        """
        if self._test_mode:
            return {
                'status': 'confirmed',
                'confirmations': 12,
                'block_number': 12345678
            }
        else:
            raise NotImplementedError(
                "Получение статуса транзакций требует настройки "
                "подключения к Ethereum RPC"
            )


class BlockchainServiceFactory:
    """Фабрика для создания сервисов блокчейна."""
    
    _services: Dict[str, type] = {
        'BTC': BitcoinService,
        'ETH': EthereumService,
    }
    
    @classmethod
    def get_service(cls, cryptocurrency_symbol: str) -> BlockchainService:
        """
        Получает сервис для работы с указанной криптовалютой.
        
        Args:
            cryptocurrency_symbol: Символ криптовалюты (BTC, ETH и т.д.)
            
        Returns:
            Экземпляр сервиса блокчейна
            
        Raises:
            ValueError: Если криптовалюта не поддерживается
        """
        symbol = cryptocurrency_symbol.upper()
        service_class = cls._services.get(symbol)
        
        if not service_class:
            raise ValueError(
                f"Криптовалюта {cryptocurrency_symbol} не поддерживается. "
                f"Доступные: {', '.join(cls._services.keys())}"
            )
        
        return service_class()
    
    @classmethod
    def register_service(
        cls,
        cryptocurrency_symbol: str,
        service_class: type
    ) -> None:
        """
        Регистрирует новый сервис блокчейна.
        
        Args:
            cryptocurrency_symbol: Символ криптовалюты
            service_class: Класс сервиса (должен наследоваться от BlockchainService)
        """
        if not issubclass(service_class, BlockchainService):
            raise TypeError(
                "Класс сервиса должен наследоваться от BlockchainService"
            )
        cls._services[cryptocurrency_symbol.upper()] = service_class


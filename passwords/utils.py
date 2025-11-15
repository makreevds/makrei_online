"""Утилиты для шифрования и расшифровки паролей."""
from typing import Optional
from cryptography.fernet import Fernet
from hashlib import sha256
import base64


def derive_key(master_password: str) -> bytes:
    """
    Генерирует ключ для шифрования на основе мастер-пароля.
    
    Использует SHA256 для создания хеша мастер-пароля,
    затем кодирует его в формат, подходящий для Fernet.
    
    Args:
        master_password: Мастер-пароль пользователя
        
    Returns:
        bytes: Ключ для шифрования Fernet
    """
    # Создаём хеш мастер-пароля
    hash_digest = sha256(master_password.encode()).digest()
    # Кодируем в base64 для Fernet (требуется 32 байта)
    key = base64.urlsafe_b64encode(hash_digest)
    return key


def encrypt_password(password: str, master_password: str) -> str:
    """
    Шифрует пароль с помощью мастер-пароля.
    
    Args:
        password: Пароль для шифрования
        master_password: Мастер-пароль для генерации ключа
        
    Returns:
        str: Зашифрованный пароль в base64 формате
    """
    key = derive_key(master_password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password: str, master_password: str) -> Optional[str]:
    """
    Расшифровывает пароль с помощью мастер-пароля.
    
    Args:
        encrypted_password: Зашифрованный пароль в base64 формате
        master_password: Мастер-пароль для генерации ключа
        
    Returns:
        str: Расшифрованный пароль или None в случае ошибки
    """
    try:
        key = derive_key(master_password)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_password.encode())
        return decrypted.decode()
    except Exception:
        return None


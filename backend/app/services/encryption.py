"""
数据加密服务 — AES-256-GCM 加密/解密
用于保护敏感数据（财务、邮件等）
"""
import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionService:
    """AES-256-GCM 加密服务"""

    def __init__(self, key: str = None):
        """初始化加密服务，key 不足32字节时自动用 SHA-256 扩展"""
        if key is None:
            from app.config.settings import settings
            key = settings.ENCRYPTION_KEY
        # 使用 SHA-256 确保 key 为 32 字节
        key_bytes = hashlib.sha256(key.encode()).digest()
        self._aesgcm = AESGCM(key_bytes)

    def encrypt(self, plaintext: str) -> str:
        """加密明文，返回 base64 编码的密文"""
        nonce = os.urandom(12)  # 96-bit nonce
        data = plaintext.encode('utf-8')
        ciphertext = self._aesgcm.encrypt(nonce, data, None)
        # nonce + ciphertext 一起编码
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt(self, encrypted: str) -> str:
        """解密 base64 编码的密文"""
        raw = base64.b64decode(encrypted.encode('utf-8'))
        nonce = raw[:12]
        ciphertext = raw[12:]
        plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')


# 全局单例
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """获取加密服务单例"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service

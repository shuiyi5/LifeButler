"""
测试数据加密服务 — AES-256 加密/解密
"""
import pytest
from app.services.encryption import EncryptionService


class TestEncryptionService:
    """加密服务测试"""

    def setup_method(self):
        self.service = EncryptionService(key="test-encryption-key-32bytes!!")

    def test_encrypt_decrypt_roundtrip(self):
        """TC-108-1: 加密后解密还原"""
        original = "这是一条敏感的财务数据"
        encrypted = self.service.encrypt(original)
        decrypted = self.service.decrypt(encrypted)
        assert decrypted == original

    def test_different_data_different_ciphertext(self):
        """TC-108-2: 不同数据加密结果不同"""
        data1 = "数据一"
        data2 = "数据二"
        encrypted1 = self.service.encrypt(data1)
        encrypted2 = self.service.encrypt(data2)
        assert encrypted1 != encrypted2

    def test_same_data_different_ciphertext(self):
        """相同数据每次加密结果不同（IV随机）"""
        data = "相同的数据"
        encrypted1 = self.service.encrypt(data)
        encrypted2 = self.service.encrypt(data)
        assert encrypted1 != encrypted2

    def test_empty_string(self):
        """空字符串加密"""
        encrypted = self.service.encrypt("")
        decrypted = self.service.decrypt(encrypted)
        assert decrypted == ""

    def test_long_data(self):
        """长数据加密"""
        data = "A" * 10000
        encrypted = self.service.encrypt(data)
        decrypted = self.service.decrypt(encrypted)
        assert decrypted == data

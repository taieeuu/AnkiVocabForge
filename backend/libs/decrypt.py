"""
解密前端传来的加密 API Key
使用与前端相同的加密方式（AES-GCM）
"""
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def derive_key(domain: str = "localhost") -> bytes:
    """派生加密密钥（与前端逻辑一致）"""
    # 使用域名 + 固定字符串作为密钥材料
    key_material = f"{domain}anki-generator-secret-key-2024".encode()
    salt = b'anki-generator-salt'
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    return kdf.derive(key_material)


def decrypt_api_key(encrypted_text: str, domain: str = "localhost") -> str:
    """
    解密前端传来的加密 API Key
    
    :param encrypted_text: 加密的 base64 字符串
    :param domain: 域名（用于派生密钥）
    :return: 解密后的 API Key
    """
    try:
        # 解码 base64
        combined = base64.b64decode(encrypted_text)
        
        # 提取 IV (前 12 字节) 和加密数据
        iv = combined[:12]
        encrypted_data = combined[12:]
        
        # 派生密钥
        key = derive_key(domain)
        
        # 解密
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(iv, encrypted_data, None)
        
        return decrypted.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decrypt API Key: {str(e)}")


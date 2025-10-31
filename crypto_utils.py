import base64, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AESCipher:
    def __init__(self, key_b64: str):
        if not key_b64:
            raise ValueError("AES256_KEY_B64 not set")
        self.key = base64.urlsafe_b64decode(key_b64)
        if len(self.key) != 32:
            raise ValueError("AES key must be 32 bytes (256-bit)")
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> str:
        nonce = os.urandom(12)
        ct = self.aesgcm.encrypt(nonce, plaintext, aad)
        return base64.urlsafe_b64encode(nonce + ct).decode()

    def decrypt(self, token_b64: str, aad: bytes = b"") -> bytes:
        raw = base64.urlsafe_b64decode(token_b64)
        nonce, ct = raw[:12], raw[12:]
        return self.aesgcm.decrypt(nonce, ct, aad)

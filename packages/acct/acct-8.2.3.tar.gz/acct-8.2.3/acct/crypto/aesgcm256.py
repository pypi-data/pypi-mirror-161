import binascii
import os
from typing import Dict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key(hub) -> str:
    """
    This is a version of `AESGCM.generate_key()` that generates a key
    that can be stored in an environment variable.
    """
    return binascii.b2a_base64(os.urandom(256 // 8)).decode("utf-8").strip()


def encrypt(hub, data: Dict, key: str) -> bytes:
    key = binascii.a2b_base64(key.encode("utf-8"))
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    raw = hub.crypto.init.dump(data)
    encrypted = aesgcm.encrypt(nonce=nonce, data=raw, associated_data=None)
    # An encrypted file is returned with the nonce as a header
    return nonce + encrypted


def decrypt(hub, data: bytes, key: str) -> Dict:
    key = binascii.a2b_base64(key.encode("utf-8"))
    # The nonce is derived from the header
    nonce = data[:12]
    data = data[12:]
    aesgcm = AESGCM(key)
    raw = aesgcm.decrypt(nonce=nonce, data=data, associated_data=None)
    return hub.crypto.init.load(raw)

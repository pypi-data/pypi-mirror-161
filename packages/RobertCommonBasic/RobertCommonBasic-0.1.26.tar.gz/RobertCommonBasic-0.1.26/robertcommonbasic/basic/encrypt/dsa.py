import base64
from Crypto.PublicKey import DSA

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key, load_der_public_key, load_der_private_key
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import dsa


def get_sign(v):
    if not v or v < 0x80:
        return v
    return v - 0x100


def get_unsign(v):
    return v & 0xff


def get_key(values: list) -> str:
    keys = bytearray(len(values))
    for i in range(len(values)):
        keys[i] = get_unsign(values[i])
    return base64.b64encode(keys).decode()


# 生成密钥对
def generate_dsa_key(bits: int = 4096, format='PEM', pkcs8=None, passphrase=None, protection=None) -> tuple:
    dsa = DSA.generate(bits)
    server_private_pem = dsa.exportKey(format=format, pkcs8=pkcs8, passphrase=passphrase, protection=protection)
    server_public_pem = dsa.publickey().exportKey(format=format, pkcs8=pkcs8, passphrase=passphrase, protection=protection)
    return server_private_pem, server_public_pem


# DSA签名
def dsa_sign(server_private_pem: bytes, content: bytes,  format: str ='PEM', algorithm: str = 'MD5') -> bytes:
    if format == 'PEM':
        private_key = load_pem_private_key(server_private_pem, password=None)
    else:
        private_key = load_der_private_key(server_private_pem, password=None)
    if isinstance(private_key, dsa.DSAPrivateKey):
        if algorithm == 'MD5':
            return private_key.sign(content, hashes.MD5())
        elif algorithm == 'SHA1':
            return private_key.sign(content, hashes.SHA1())
        elif algorithm == 'SHA224':
            return private_key.sign(content, hashes.SHA224())
        elif algorithm == 'SHA256':
            return private_key.sign(content, hashes.SHA256())
        elif algorithm == 'SHA384':
            return private_key.sign(content, hashes.SHA384())
        elif algorithm == 'SHA512':
            return private_key.sign(content, hashes.SHA512())
    raise Exception(f"dsa sign fail")


# DSA验签
def dsa_verify(server_public_pem: bytes, decrypt_content: bytes, sign_content: bytes, format: str ='PEM', algorithm: str = 'MD5'):
    if format == 'PEM':
        public_key = load_pem_public_key(server_public_pem, backend=default_backend())
    else:
        public_key = load_der_public_key(server_public_pem, backend=default_backend())
    if isinstance(public_key, dsa.DSAPublicKey):
        try:
            if algorithm == 'MD5':
                public_key.verify(sign_content, decrypt_content, hashes.MD5())
            elif algorithm == 'SHA1':
                public_key.verify(sign_content, decrypt_content, hashes.SHA1())
            elif algorithm == 'SHA224':
                public_key.verify(sign_content, decrypt_content, hashes.SHA224())
            elif algorithm == 'SHA256':
                public_key.verify(sign_content, decrypt_content, hashes.SHA256())
            elif algorithm == 'SHA384':
                public_key.verify(sign_content, decrypt_content, hashes.SHA384())
            elif algorithm == 'SHA512':
                public_key.verify(sign_content, decrypt_content, hashes.SHA512())
        except InvalidSignature:
            return False
        return True
    return False
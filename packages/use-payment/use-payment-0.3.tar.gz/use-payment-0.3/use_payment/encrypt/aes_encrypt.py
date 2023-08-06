import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AesDecryptError(Exception):
    """aes解密错误"""


def aes_decrypt(key: str, ciphertext: str, nonce: str, associated_data: str = '') -> str:
    """AES解密 失败抛异常"""
    key_bytes = str.encode(key)
    nonce_bytes = str.encode(nonce)
    ad_bytes = str.encode(associated_data)
    data = base64.b64decode(ciphertext)
    aesgcm = AESGCM(key_bytes)
    try:
        return aesgcm.decrypt(nonce_bytes, data, ad_bytes).decode('utf-8')
    except Exception as err:
        raise AesDecryptError(f'aes解密错误：{err.__class__.__name__}')


def aes_encrypt(key: str, plaintext: str, nonce: str, associated_data: str = '') -> str:
    """AES加密 失败抛异常"""
    key_bytes = str.encode(key)
    nonce_bytes = str.encode(nonce)
    associated_data_bytes = str.encode(associated_data)
    aesgcm = AESGCM(key_bytes)
    ciphertext_bytes = aesgcm.encrypt(nonce_bytes, plaintext.encode('utf-8'), associated_data_bytes)
    return base64.b64encode(ciphertext_bytes).decode('utf-8')


# if __name__ == '__main__':
#     encrypt_text = aes_encrypt('15028d056ce5296c', '{"code":"Python"}', '123456788', '1235')
#     print(encrypt_text)
#     plain_text = aes_decrypt('15028d056ce5296c', 'fbbo1PUUNWausK5qMy0GN5R23uS8Xxc2iFZViO9rMMrR', '123456788', '1235')
#     print(plain_text)

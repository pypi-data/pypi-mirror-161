from base64 import b64decode, b64encode
from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP, PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, SHA256, SM3, Hash
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


class LoadPrivateKeyError(Exception):
    """load_pem_private_key 载入密钥错误"""


class LoadCertificateError(Exception):
    """load_pem_x509_certificate 载入证书错误"""


class LoadPublicKeyError(Exception):
    """load_pem_public_key 载入公钥错误"""


def rsa_sign(msg_string: str, private_key: str) -> str:
    message = msg_string.encode('UTF-8')
    try:
        private_key = load_pem_private_key(data=private_key.encode('UTF-8'), password=None, backend=default_backend())
    except Exception as err:
        raise LoadPrivateKeyError('private_key格式可能错误')
    signature = private_key.sign(data=message, padding=PKCS1v15(), algorithm=SHA256())
    sign = b64encode(signature).decode('UTF-8').replace('\n', '')
    return sign


def rsa_verify(msg_string: str, signature: str, cert_str: str) -> bool:
    try:
        certificate = load_pem_x509_certificate(data=cert_str.encode('UTF-8'), backend=default_backend())
    except Exception as err:
        raise LoadCertificateError('cert_str格式可能错误')
    public_key = certificate.public_key()
    # public_key.public_bytes(encoding=Encoding.PEM, format=PublicFormat.PKCS1) #提取证书中的public_key
    message = msg_string.encode('UTF-8')
    signature = b64decode(signature)
    try:
        public_key.verify(signature, message, PKCS1v15(), SHA256())
    except InvalidSignature:
        return False
    return True


def rsa_verify_by_public_key(msg_string: str, signature: str, public_key: str) -> bool:
    message = msg_string.encode('UTF-8')
    signature = b64decode(signature)
    try:
        public_key = load_pem_public_key(data=public_key.encode('UTF-8'))
    except Exception as err:
        raise LoadPublicKeyError('public_key格式可能错误')
    try:
        public_key.verify(signature, message, PKCS1v15(), SHA256())
    except InvalidSignature:
        return False
    return True

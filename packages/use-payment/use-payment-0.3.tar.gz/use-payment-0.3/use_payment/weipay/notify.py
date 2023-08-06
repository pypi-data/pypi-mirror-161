import json
from typing import Callable
from .weipay import V3_KEY
from .v3_cert import V3Cert
from ..encrypt.rsa_encrypt import rsa_verify
from ..encrypt.aes_encrypt import aes_decrypt, AesDecryptError
from ..exceptions import *

__all__ = ['notify_verify', 'notify_process']


def notify_verify(headers: dict, response_str: str) -> bool:
    """微信支付回调通知的签名验证"""
    timestamp = headers['Wechatpay-Timestamp']
    nonce = headers['Wechatpay-Nonce']
    signature = headers['Wechatpay-Signature']
    serial_no = headers['Wechatpay-Serial']
    structure_string = f'{timestamp}\n{nonce}\n{response_str}\n'
    cert_list = V3Cert().cert_list  # 证书有可能为空（获取证书失败失败）
    for cert_dict in cert_list:
        if serial_no != cert_dict['serial_no']:
            continue
        if rsa_verify(structure_string, signature, cert_dict['cert_str']):
            return True
    return False


def _aes_decrypt_notify(response_dict: dict) -> str:
    """微信支付回调报文解密"""
    resource = response_dict['resource']
    nonce = resource['nonce']
    associated_data = resource['associated_data']
    ciphertext = resource['ciphertext']
    return aes_decrypt(V3_KEY, ciphertext, nonce, associated_data)


def notify_process(headers: dict, response_bytes: bytes, callback: Callable) -> dict:
    try:
        res_json = json.loads(response_bytes)
    except json.JSONDecodeError:
        raise NotifyVerifyError('微信支付通知json.loads(response_bytes)失败')

    if not notify_verify(headers, response_bytes.decode('UTF-8')):
        raise NotifyVerifyError('微信支付通知回验错误')
    try:
        notify = _aes_decrypt_notify(res_json)
    except AesDecryptError:
        raise NotifyVerifyError('微信支付通知ciphertext解密错误')

    callback(notify)

    return json.loads(notify)

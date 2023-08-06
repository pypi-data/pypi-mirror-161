import time
from typing import *
from .weipay import V3_KEY, RequestCert, RequestCertError
from ..encrypt.aes_encrypt import aes_decrypt

__all__ = ['V3Cert']


class V3Cert:
    """微信支付 V3证书列表，超过6小时从服务器获取 用于微信支付回调通知的签名验证
    # 获取v3证书列表->[{'serial_no':xxx, 'cert_str':xxx}]
    cert_list:List[Dict[str,str] = V3Cert().cert_list #获取失败时为空
    """
    last_request_time: int = 0  # 最近一次请求时间(10位时间戳)
    cert_list: List[dict] = []

    def __init__(self):
        # 大于6小时需要重新获取证书
        if int(time.time()) - self.last_request_time > 3600 * 6:
            self._request_cert()

    def _request_cert(self):
        """从服务器请求证书"""
        try:
            cert_list = RequestCert().cert_list()
        except RequestCertError:
            return
        for cert_itm in cert_list:
            serial_no = cert_itm['serial_no']
            encrypt_cert = cert_itm['encrypt_certificate']
            ciphertext = encrypt_cert['ciphertext']
            nonce = encrypt_cert['nonce']
            associated_data = encrypt_cert['associated_data']
            # 解密获取到证书字符串
            try:
                cert_string = aes_decrypt(V3_KEY, ciphertext, nonce, associated_data)
            except Exception:
                continue
            self.__class__.cert_list.append({'serial_no': serial_no, 'cert_str': cert_string})
        self.__class__.last_request_time = int(time.time())

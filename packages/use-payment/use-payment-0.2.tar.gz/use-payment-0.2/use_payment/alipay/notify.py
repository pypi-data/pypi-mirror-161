import copy
from .alipay import PUBLIC_KEY
from ..exceptions import *
from ..encrypt.rsa_encrypt import rsa_verify_by_public_key
from typing import Callable

__all__ = ['notify_verify', 'notify_process']


def notify_verify(notify_data: dict) -> bool:
    """
    异步验签
    :param notify_data:异步回调POST数据
    :return:bool
    """
    notify_data = copy.deepcopy(notify_data)
    sign = notify_data.pop('sign', 'null')  # 取出sign
    notify_data.pop('sign_type', None)  # 取出sign_type
    unsigned_string = '&'.join((f'{key}={value}' for key, value in sorted(notify_data.items())))
    return rsa_verify_by_public_key(unsigned_string, sign, PUBLIC_KEY)


def notify_process(notify_data: dict, callback: Callable) -> dict:
    """
    处理支付通知，验证成功后调用callback
    :param notify_data:异步回调POST数据
    :param callback:验证成功后调用该函数，通知数据作为参数传入callback
    :return:
    """
    if not notify_verify(notify_data):
        raise NotifyVerifyError('支付宝通知回验错误')
    callback(notify_data)
    return notify_data

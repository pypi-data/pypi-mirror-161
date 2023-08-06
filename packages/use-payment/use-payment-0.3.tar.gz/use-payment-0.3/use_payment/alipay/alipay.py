"""开发文档 https://opendocs.alipay.com/open/028r8t?scene=22"""
import json
import copy
import datetime
import requests
from django.conf import settings
from importlib import import_module
from ..encrypt.rsa_encrypt import rsa_sign
from urllib.parse import quote_plus
from ..exceptions import *

__all__ = ['AliPayTradePage',
           'AliPayTradeWap',
           'AliPayRefund',
           'AliPayRefundQuery',
           'AliPayTradeQuery',
           'AliPayCloseTrade']

CONF = import_module(settings.ALIPAY_CONF)
APP_ID = CONF.APP_ID  # 应用ID
PRIVATE_KEY = CONF.PRIVATE_KEY  # 私钥
PUBLIC_KEY = CONF.PUBLIC_KEY  # 公钥
PAY_RETURN_URL = CONF.PAY_RETURN_URL  # 支付成功同步回调地址
PAY_NOTIFY_URL = CONF.PAY_NOTIFY_URL  # 支付成功异步回调地址


# 业务类继承该类
class AliPay:
    """"继承AliPay，定制业务类
    
    # 定义一个PC支付类
    class AliPayTradePage(AliPay):
        # 业务类的公共参数，AliPay已经定义了常见的公共参数，特殊的公共参数可以定义到业务类的类属性中
        method = 'alipay.trade.page.pay'

        # return_url和notify_url就是AliPayTradePage类的特殊公共参数
        return_url = 'http://apimedicine.ccwjobs.com/score/test'
        notify_url = 'http://apimedicine.ccwjobs.com/score/test'


    # 再定义一个退款类
    class AliPayTradeRefund(AliPay):
        method = 'alipay.trade.refund'

    """
    _private_key = PRIVATE_KEY  # 私有属性务必单下划线开头
    _public_key = PUBLIC_KEY
    _gateway = 'https://openapi.alipaydev.com/gateway.do'
    # 公共参数定义到类中
    app_id = APP_ID
    method = 'alipay.trade.page.pay'
    charset = 'utf-8'
    sign_type = 'RSA2'
    version = '1.0'

    def __init__(self, business_params: dict):
        self.business_params: dict = business_params  # 业务参数
        self.request_params = self._generate_request_params()  # 生成请求params

    def api_response(self) -> dict:
        """
        访问request_url返回response.json()
        :return:response.json()
        """
        request_url = self.build_url()
        try:
            res = requests.get(url=request_url, timeout=3)
        except Exception as err:
            raise RequestError(f'请求支付宝API错误:{err}')
        res_json: dict = res.json()  # 支付宝接口无论成功失败返回的都是json
        # 取出第一个键名以_response后缀的值
        res_json = next(v for k, v in res_json.items() if k.endswith('_response'))
        if res_json.get('msg') == 'Success':
            return res.json()
        else:
            raise StatusCodeError(res_json['sub_msg'])

    def build_url(self):
        """生成访问URL"""
        params = copy.deepcopy(self.request_params)
        # 生成添加签名
        params['sign'] = self._generate_sign(self.request_params)
        return self._gateway + '?' + '&'.join((f'{key}={quote_plus(value)}' for key, value in sorted(params.items())))

    def _generate_request_params(self) -> dict:
        """生成请求参数字典"""
        params = self._public_params()  # 获取公共参数
        params['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 业务参数中去掉为None的值
        params['biz_content'] = json.dumps({k: v for k, v in self.business_params.items() if v})
        return params

    def _public_params(self) -> dict:
        """没有下划线开头的类属性当作公共参数"""
        mro = [cls for cls in self.__class__.mro()[::-1] if cls is not object]
        public_params = {}
        for cls in mro:
            for key, value in cls.__dict__.items():
                # 如果参数的值为空不参与签名,参数名为下划线开头也不参与签名
                if value and isinstance(value, str) and not str(key).startswith('_'):
                    public_params[key] = value
        return public_params

    def _generate_sign(self, request_params: dict) -> str:
        """
        生成签名
        :param request_params:请求参数
        :return:加密字符串
        """
        # 排序后组合成待加密字符串 &key=value&...
        unsigned_string = '&'.join((f'{key}={value}' for key, value in sorted(request_params.items())))
        return rsa_sign(unsigned_string, self._private_key)


# PC支付
class AliPayTradePage(AliPay):
    """PC支付"""
    method = 'alipay.trade.page.pay'
    return_url = PAY_RETURN_URL
    notify_url = CONF.PAY_NOTIFY_URL

    def pay_url(self):
        return self.build_url()


# 移动支付
class AliPayTradeWap(AliPayTradePage):
    """移动支付"""
    method = 'alipay.trade.wap.pay'


# 关闭订单
class AliPayCloseTrade(AliPay):
    """关闭订单"""
    method = 'alipay.trade.close'

    def close_trade(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise CloseTradeError(err)


# 订单查询
class AliPayTradeQuery(AliPay):
    """订单查询，与微信支付不同的是，微信支付在生成pay_url后就可以查询订单，支付宝需要用户扫码后才能查询订单"""
    method = 'alipay.trade.query'

    def trade_query(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise TradeQueryError(err)


# 退款
class AliPayRefund(AliPay):
    """退款"""
    method = 'alipay.trade.refund'

    def refund(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise RefundError(err)


# 查询退款
class AliPayRefundQuery(AliPay):
    """查询退款"""
    method = 'alipay.trade.fastpay.refund.query'

    def refund_query(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise RefundQueryError(err)

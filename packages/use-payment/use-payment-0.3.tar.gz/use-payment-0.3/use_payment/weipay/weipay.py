"""开发文档 https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_3_1.shtml"""
import re
import time
import json
import random
import requests
from django.conf import settings
from importlib import import_module
from ..encrypt.rsa_encrypt import rsa_sign
from ..exceptions import *

__all__ = ['WeiPay',
           'WeiPayNative',
           'WeiPayH5',
           'WeiPayCloseTrade',
           'WeiPayTradeQuery',
           'WeiPayRefund',
           'WeiPayRefundQuery',
           'WeiPayJSAPITrade']

CONF = import_module(settings.WEIPAY_CONF)
MCHID = CONF.MCHID
APP_ID = CONF.APP_ID
SERIAL_NO = CONF.SERIAL_NO  # 证书序列号
PRIVATE_KEY = CONF.PRIVATE_KEY
V3_KEY = CONF.V3_KEY
PAY_NOTIFY_URL = CONF.PAY_NOTIFY_URL  # 支付成功异步回调地址
REFUND_NOTIFY_URL = CONF.REFUND_NOTIFY_URL  # 退款异步回调地址
# 有时候业务类会从父类继承一些不需要的参数，这时可以使用值NOT_REQUIRED来覆盖，当param = NOT_REQUIRED时param将被或略不会当作请求参数。
NOT_REQUIRED = object()


class WeiPay:
    """微信支付文档中并没有所谓的公共参数，这里的公共参数，是指那些不随着业务变化而变化的参数"""
    # 每个业务子类url都不同, 业务子类需要重新定义_url
    _url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/h5'
    # 每个业务子类method都可能不同, 业务子类可能需要重新定义_method
    _method = 'POST'
    _private_key = PRIVATE_KEY
    _serial_no = SERIAL_NO  # 证书序列号
    # 并非所有接口都需要商户号，因此下划线开头当作私有属性，供类方法调用。如果业务子类需要商户号，还需要另外定义一个不带下划线的mchid属性当作公共参数
    _mchid = MCHID  # 商户号

    def __init__(self, business_params: dict):
        self.business_params = business_params
        self.request_params = self._get_request_params()
        self.request_params.update(business_params)

    def api_response(self) -> dict:
        """请求API（根据method自动调用self.post_request或get_request），并返回response.json()
        :return: response.json()
        """
        res = getattr(self, f'{self._method.lower()}_request')()
        try:
            res_json = res.json()
        except json.JSONDecodeError:
            res_json = {}
        if res.status_code == 200:
            return res_json
        else:
            raise StatusCodeError(res_json.get('message', f'无数据（Http状态码为{res.status_code}）'))

    def post_request(self):
        """POST请求API"""
        url = self._url
        path_params = self._path_params()  # path中的参数
        url = url.format(**path_params)
        body_params = self._body_query_params(path_params)  # body中的参数
        authorization = self._generate_token(url, request_body=json.dumps(body_params))
        try:
            resp = requests.post(url, json=body_params, headers={'Authorization': authorization}, timeout=3)
        except Exception as err:
            raise RequestError(f'请求API错误:{err}')

        return resp

    def get_request(self):
        """GET请求API"""
        url = self._url
        path_params = self._path_params()  # path中的参数
        query_params = self._body_query_params(path_params)  # query中的参数
        query_string = '&'.join((f'{k}={v}' for k, v in query_params.items()))
        url = url.format(**path_params)
        url = url + '?' + query_string
        authorization = self._generate_token(url)
        try:
            resp = requests.get(url, headers={'Authorization': authorization}, timeout=3)
        except Exception as err:
            raise RequestError(err)
        return resp

    def _get_request_params(self) -> dict:
        """没有下划线开头的类属性当作请求参数"""
        request_params = {}
        # 非参数列表
        non_param = ('url', 'method')
        mro = [cls for cls in self.__class__.mro()[::-1] if cls is not object]
        for cls in mro:
            for key, value in cls.__dict__.items():
                if not any((key.startswith('_'), callable(value), key in non_param)):
                    request_params[key] = value
        # 去掉没有值的项目
        request_params = {k: v for k, v in request_params.items() if v is not NOT_REQUIRED}
        return request_params

    def _path_params(self):
        """path中的参数"""
        return {key: self.request_params[key] for key in re.findall(r'{([a-zA-Z0-9_]+)}', self._url)}

    def _body_query_params(self, path_params: dict):
        """
        query中的参数
        :param path_params:path中的参数
        :return:从request_params中过滤掉path_params中存在的参数
        """
        return {k: v for k, v in self.request_params.items() if k not in path_params}

    def _generate_token(self, url: str, request_body: str = '') -> str:
        """
        生成请求的token （放在authorization中）
        :param url:并去除域名部分得到参与签名的UR,如果请求中有查询参数，URL末尾应附加有'?'和对应的查询字符串。
        :param request_body:请求方法为GET时，报文主体为空,当请求方法为POST或PUT时，请使用真实发送的JSON报文。
        :return:密文
        """
        url = url.replace('https://api.mch.weixin.qq.com', '')
        timestamp = str(int(time.time()))
        random_str = ''.join(random.sample('ABCDEFGHIJKLMNOPQISTUVWXYZ0123456789', 20))
        unsigned_string = f"{self._method}\n{url}\n{timestamp}\n{random_str}\n{request_body}\n"
        signature = rsa_sign(unsigned_string, self._private_key)
        return f'WECHATPAY2-SHA256-RSA2048 mchid="{self._mchid}",nonce_str="{random_str}",' \
               f'signature="{signature}",timestamp="{timestamp}",serial_no="{self._serial_no}"'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.business_params})'


# H5下单
class WeiPayH5(WeiPay):
    """微信支付H5下单"""
    _url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/h5'
    _method = 'POST'
    appid = APP_ID
    mchid = MCHID  # 直连商户号
    scene_info = {'payer_client_ip': '0.0.0.0', 'h5_info': {'type': 'Wap'}}
    notify_url = PAY_NOTIFY_URL  # 通知地址

    def pay_url(self):
        """获取付款URL"""
        try:
            return self.api_response()['h5_url']
        except StatusCodeError as err:
            raise TradeError(err)


# Native下单
class WeiPayNative(WeiPayH5):
    """微信支付Native下单"""
    _url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/native'
    scene_info = NOT_REQUIRED  # 从WeiPayH5了scene_info，但是本接口不需要因此使用值NOT_REQUIRED来替代·

    def pay_url(self):
        """获取付款URL"""
        try:
            return self.api_response()['code_url']
        except StatusCodeError as err:
            raise TradeError(err)


# 关闭订单
class WeiPayCloseTrade(WeiPay):
    """关闭订单"""
    _url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/out-trade-no/{out_trade_no}/close'
    _method = 'POST'
    mchid = MCHID  # 直连商户号

    def close_trade(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise CloseTradeError(err)


# 商户订单号查询订单
class WeiPayTradeQuery(WeiPay):
    """订单查询，与支付宝不同的是，微信支付在生成pay_url后就可以查询订单，支付宝需要用户扫码后才能查询订单"""
    _url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/out-trade-no/{out_trade_no}'
    _method = 'GET'
    mchid = MCHID  # 直连商户号

    def trade_query(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise TradeQueryError(err)


# 订单退款
class WeiPayRefund(WeiPay):
    """退款"""
    _url = 'https://api.mch.weixin.qq.com/v3/refund/domestic/refunds'
    _method = 'POST'
    notify_url = 'http://apimedicine.ccwjobs.com/score/test'

    def refund(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise RefundError(err)


# 退款查询
class WeiPayRefundQuery(WeiPay):
    """退款查询"""
    _url = 'https://api.mch.weixin.qq.com/v3/refund/domestic/refunds/{out_refund_no}'
    _method = 'GET'

    def refund_query(self):
        try:
            return self.api_response()
        except StatusCodeError as err:
            raise RefundQueryError(err)


class RequestCert(WeiPay):
    """请求V3证书"""
    _url = 'https://api.mch.weixin.qq.com/v3/certificates'
    _method = 'GET'
    serial_no = SERIAL_NO

    def __init__(self):
        super().__init__({'serial_no': self.serial_no})

    def cert_list(self):
        try:
            result = self.api_response()
            return result.get('data')
        except StatusCodeError as err:
            raise RequestCertError(err)


# 定义一个微信支付业务类
# 定义一个JSAPI下单类首先继承WeiPay ,WeiPay的__init__接受一个业务参数字典
class WeiPayJSAPITrade(WeiPay):
    # 定义请求的URL和Method ,注意一定下划线开头，否则会被认为是业务固定参数，
    _url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'
    _method = 'POST'

    # 固定参数声明,与支付宝的公共参数不同，微信支付没有作用于所有API的公共参数，但是每个业务API都可能存在某些固定参数，（固定参数就是那些不随业务变化而变化的参数）
    appid = APP_ID
    mchid = MCHID  # 直连商户号
    notify_url = REFUND_NOTIFY_URL  # 通知地址

    # 定义一个接口函数，名称建议有直白含义
    def prepay_id(self):
        try:
            return self.api_response()['prepay_id']  # 访问api获得响应数据
        except StatusCodeError as err:
            raise TradeQueryError(err)  # 抛出与当前业务抽象一致的异常

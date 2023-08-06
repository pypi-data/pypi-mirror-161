class RequestError(Exception):
    """请求api失败"""


class RefundError(Exception):
    """退款失败"""


class TradeError(Exception):
    """下单获取pay_url失败"""


class TradeQueryError(Exception):
    """订单查询失败"""


class RefundQueryError(Exception):
    """退款查询失败"""


class StatusCodeError(Exception):
    """状态码非200"""


class SignVerifyError(Exception):
    """签名回验错误"""


class CloseTradeError(Exception):
    """关闭订单失败"""


class RequestCertError(Exception):
    """微信支付，请求证书失败"""


class NotifyVerifyError(Exception):
    """通知回验校验失败"""

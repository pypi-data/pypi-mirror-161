from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation

__all__ = ['TradeParams',
           'RefundParams',
           'TradeQueryParams',
           'RefundQueryParams',
           'CloseTradeParams',
           'JSAPIParams',
           ]


# 元类的__call__会让使用它的类的__init__中的参数注解信息失效（__call__会覆盖__init__），因此废弃
class ParamsMeta(type, ABC):
    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        if self.pay_web == 'alipay':
            return self.ali_params()
        elif self.pay_web == 'weipay':
            return self.wei_params()
        else:
            raise ValueError(f'错误的pay_web：{self.pay_web}，pay_web的值目前只能为alipay或weipay')


# 所有参数类的抽象基类
class ParamsABC(ABC):

    @property
    def params(self) -> dict:
        pay_web = getattr(self, 'pay_web')
        if pay_web == 'alipay':
            return self.ali_params()
        elif pay_web == 'weipay':
            return self.wei_params()
        else:
            raise ValueError(f'错误的pay_web：{pay_web}，pay_web的值目前只能为alipay或weipay')

    @abstractmethod
    def ali_params(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def wei_params(self) -> dict:
        raise NotImplementedError

    def __subclasshook__(self):
        for attr in ('pay_web', 'wei_params', 'ali_params', 'params'):
            if not hasattr(self, attr):
                return NotImplemented
        return True


# 下单收款业务参数类
class TradeParams(ParamsABC):

    def __init__(self,
                 pay_web: str,
                 out_trade_no: str,
                 total_amount: str,
                 subject: str,
                 extend: dict = None):
        """
        注意：经过元类处理，Trade的实例最终是个业务参数字典
        :param pay_web:支付平台 alipay或者weipay
        :param out_trade_no:商户订单号
        :param total_amount:交易总金额
        :param subject:交易标题描述
        :param extend:extend用于扩展业务参数字典
        """
        self.pay_web = pay_web
        self.out_trade_no = out_trade_no
        self.total_amount = total_amount
        self.subject = subject
        self.extend = {} if extend is None else extend

    def ali_params(self):
        # goods_detail: List[dict]
        return {'out_trade_no': self.out_trade_no,
                'total_amount': self.total_amount,
                'subject': self.subject,
                'product_code': 'FAST_INSTANT_TRADE_PAY'}

    def wei_params(self):
        try:
            total_amount = int(Decimal(self.total_amount) * 100)
        except InvalidOperation:
            raise ValueError(f'total_amount:{self.total_amount}不能转化为Decimal')

        return {
            'out_trade_no': self.out_trade_no,
            'amount': {'total': total_amount},
            'description': self.subject,
            # 必填项，采用无关紧要的默认值 由于该参数采用固定默认值，故放置到类的定义中
            # 'scene_info': {'payer_client_ip': '0.0.0.0', 'h5_info': {'type': 'Wap'}}
        }


# 退款业务参数类
class RefundParams(ParamsABC):
    def __init__(self, pay_web: str, out_trade_no: str, out_refund_no, amount: str, total: str = None, reason=''):
        """
        :param pay_web: 支付平台
        :param out_trade_no: 商户订单号
        :param out_refund_no:退款单号
        :param amount:退款金额
        :param total:订单金额，微信支付退款时必填,支付宝选填
        :param reason:退款原因，选填
        """
        self.pay_web = pay_web
        self.out_trade_no = out_trade_no
        self.out_refund_no = out_refund_no
        self.amount = amount
        self.total = total
        self.reason = reason

    def ali_params(self) -> dict:
        amount = str(self.amount)
        return {'out_trade_no': self.out_trade_no, 'refund_amount': amount,
                'out_request_no': self.out_refund_no, 'refund_reason': self.reason}

    def wei_params(self) -> dict:
        try:
            amount = int(Decimal(self.amount) * 100)
        except InvalidOperation:
            raise ValueError(f'amount:{self.amount}不能转化为Decimal')

        try:
            total = int(Decimal(self.total) * 100)
        except InvalidOperation:
            raise ValueError(f'total:{self.total}不能转化为Decimal')

        if not self.reason:
            raise ValueError('微信支付退款原因reason必填')
        return {'out_trade_no': self.out_trade_no, 'out_refund_no': self.out_refund_no,
                'reason': self.reason, 'amount': {'refund': amount, 'total': total, 'currency': 'CNY'}}


# 定义一个订单查询的业务参数类，
# 订单查询
class TradeQueryParams(ParamsABC):  # 继承PayParams抽象类
    # 必须指定pay_web，会根据pay_web来决定生成微信支付还是支付宝格式
    def __init__(self, pay_web: str, out_trade_no: str):
        """
        :param pay_web: 支付平台
        :param out_trade_no: 商户订单号
        """
        self.pay_web = pay_web
        self.out_trade_no = out_trade_no

    # 必须实现的抽象方法ali_params
    def ali_params(self) -> dict:
        return {'out_trade_no': self.out_trade_no}

    # 必须实现的抽象方法wei_params
    def wei_params(self) -> dict:
        return self.ali_params()


# 退款查询参数类
class RefundQueryParams(ParamsABC):
    def __init__(self, pay_web: str, out_request_no: str, out_trade_no: str = None):
        """
        :param pay_web:支付平台
        :param out_request_no:退款请求号
        :param out_trade_no:商户订单号 微信支付可选，支付宝必选
        """
        self.pay_web = pay_web
        self.out_request_no = out_request_no
        self.out_trade_no = out_trade_no

    def ali_params(self) -> dict:
        if self.out_trade_no is None:
            raise ValueError('RefundQueryParam out_trade_no的值不能为None')
        return {'out_trade_no': self.out_trade_no, 'out_request_no': self.out_request_no,
                'query_options': ['deposit_back_info']}

    def wei_params(self) -> dict:
        return {'out_refund_no': self.out_request_no}


# 关闭订单参数
class CloseTradeParams(TradeQueryParams):
    def __init__(self, pay_web: str, out_trade_no: str):
        """
        :param pay_web: 支付平台
        :param out_trade_no: 商户订单号
        """
        super().__init__(pay_web, out_trade_no)


class JSAPIParams(TradeParams):
    """微信支付JSAPI下单参数"""

    def __init__(self,
                 pay_web: str,
                 out_trade_no: str,
                 total_amount: str,
                 subject: str,
                 openid: str):
        super().__init__(pay_web, out_trade_no, total_amount, subject)
        self.openid = openid

    def wei_params(self):
        _params = super().wei_params()
        _params['payer'] = {'openid': self.openid}
        return _params

    def ali_params(self):
        raise ValueError('该参数类不用于支付宝模块')

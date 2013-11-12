# -*- coding: utf-8 -*-
import md5
import urllib
import requests
from .exceptions import MissingParameter
from .exceptions import ParameterValueError


class Alipay(object):

    GATEWAY_URL = 'https://mapi.alipay.com/gateway.do'

    def __init__(self, pid, key, seller_email):
        self.key = key
        self.pid = pid
        self.default_params = {'_input_charset': 'utf-8',
                               'partner': pid,
                               'seller_email': seller_email,
                               'payment_type': '1'}

    def _generate_sign(self, params):
        src = '&'.join(['%s=%s' % (key, value) for key,
                        value in sorted(params.iteritems())]) + self.key
        return md5.new(src).hexdigest()

    def _check_params(self, params, names):
        if not all(k in params for k in names):
            raise MissingParameter('missing parameters')
        return

    def _build_url(self, service, **kw):
        params = self.default_params.copy()
        params['service'] = service
        params.update(kw)
        params.update({'sign_type': 'MD5',
                       'sign': self._generate_sign(params)})

        return '%s?%s' % (self.GATEWAY_URL, urllib.urlencode(params))

    def create_direct_pay_by_user_url(self, **kw):
        '''即时到帐'''
        self._check_params(kw, ['out_trade_no', 'subject'])

        if not kw.get('total_fee') and \
           not (kw.get('price') and kw.get('quantity')):
            raise ParameterValueError('total_fee or (price && quantiry)\
             must have one')

        url = self._build_url('create_direct_pay_by_user', **kw)
        return url

    def create_partner_trade_by_buyer_url(self, **kw):
        '''担保交易'''
        names = ['out_trade_no', 'subject', 'logistics_type',
                 'logistics_fee', 'logistics_payment', 'price', 'quantity']
        self._check_params(kw, names)
        url = self._build_url('create_partner_trade_by_buyer', **kw)
        return url

    def trade_create_by_buyer_url(self, **kw):
        '''标准双接口'''
        names = ['out_trade_no', 'subject', 'logistics_type',
                 'logistics_fee', 'logistics_payment', 'price', 'quantity']
        self._check_params(kw, names)

        url = self._build_url('trade_create_by_buyer', **kw)
        return url

    def verify_notify(self, **kw):
        sign = kw.pop('sign')
        kw.pop('sign_type')
        if self._generate_sign(kw) == sign:
            return requests.get("https://mapi.alipay.com/gateway.do?service=notify_verify&partner=%s&notify_id=%s" % (self.pid, kw['notify_id'])).text == 'true'
        else:
            return False

from __future__ import print_function

import datetime
import hashlib
import hmac
import urllib.parse
from collections import OrderedDict
from urllib.parse import urlparse

from requests.auth import AuthBase

__version__ = '0.4'


class AWSSigV4(AuthBase):
    """AWS签名流程 https://docs.aws.amazon.com/zh_cn/general/latest/gr/sigv4-create-canonical-request.html"""

    def __init__(self, service, **kwargs):
        self.service = service
        self.aws_access_key_id = kwargs.get('aws_access_key_id')
        self.aws_secret_access_key = kwargs.get('aws_secret_access_key')
        self.aws_session_token = kwargs.get('aws_session_token')
        if self.aws_access_key_id is None or self.aws_secret_access_key is None:
            raise KeyError("AWS Access Key ID and Secret Access Key are required")
        self.region = kwargs.get('region')
        self.request = None

    @staticmethod
    def sign_msg(key, msg):
        """Sign message using key"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _build_method(self):
        return self.request.method

    def _build_query_string(self):
        p = urlparse(self.request.url)
        if len(p.query) > 0:
            qs = dict(map(lambda i: i.split('='), p.query.split('&')))
        else:
            qs = dict()

        return "&".join(map(lambda x: '='.join(x), sorted(qs.items())))

    def _build_headers(self):
        headers_to_sign = {'host': self.host, 'x-amz-date': self.amzdate}
        if self.aws_session_token is not None:
            headers_to_sign['x-amz-security-token'] = self.aws_session_token

        ordered_headers = OrderedDict(sorted(headers_to_sign.items(), key=lambda t: t[0]))
        canonical_headers = ''.join(map(lambda h: ":".join(h) + '\n', ordered_headers.items()))
        signed_headers = ';'.join(ordered_headers.keys())

        return canonical_headers, signed_headers

    def _build_payload(self):
        if self.request.method == 'GET':
            payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()
        else:
            if self.request.body:
                payload_hash = hashlib.sha256(self.request.body.encode('utf-8')).hexdigest()
            else:
                payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()

        return payload_hash

    def _build_request(self):
        p = urlparse(self.request.url)
        # 1. HTTP 请求方法
        method = self._build_method()
        # 2. URI
        uri = urllib.parse.quote(p.path)
        # 3. 查询字符串
        canonical_querystring = self._build_query_string()
        # 4. 添加规范标头
        canonical_headers, signed_headers = self._build_headers()
        # 5. 负载的哈希值
        payload_hash = self._build_payload()

        canonical_request = '\n'.join([method, uri, canonical_querystring,
                                       canonical_headers, signed_headers, payload_hash])

        return canonical_request, signed_headers

    def _build_authorization_header(self):
        canonical_request, signed_headers = self._build_request()

        credential_scope = '/'.join([self.datestamp, self.region, self.service, 'aws4_request'])

        string_to_sign = '\n'.join(['AWS4-HMAC-SHA256', self.amzdate,
                                    credential_scope, hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()])

        kDate = self.sign_msg(('AWS4' + self.aws_secret_access_key).encode('utf-8'), self.datestamp)
        kRegion = self.sign_msg(kDate, self.region)
        kService = self.sign_msg(kRegion, self.service)
        kSigning = self.sign_msg(kService, 'aws4_request')
        signature = hmac.new(kSigning, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        authorization_header = "AWS4-HMAC-SHA256 Credential={}/{}, SignedHeaders={}, Signature={}".format(
            self.aws_access_key_id, credential_scope, signed_headers, signature)

        return authorization_header

    def __call__(self, r):
        self.request = r
        p = urlparse(self.request.url)
        self.host = p.hostname

        t = datetime.datetime.utcnow()
        self.amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        self.datestamp = t.strftime('%Y%m%d')

        r.headers.update({
            'host': self.host,
            'x-amz-date': self.amzdate,
            'Authorization': self._build_authorization_header(),
            'x-amz-security-token': self.aws_session_token
        })
        return r

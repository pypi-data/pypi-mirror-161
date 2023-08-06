import json
import time
import uuid
from datetime import datetime
from urllib.parse import urlparse

import boto3
import requests

from spapi.aws_sig_v4 import AWSSigV4
from spapi.cache import cache
from spapi.credential_provider import CredentialProvider
from spapi.exceptions import SPAPIClientIdNotInWhiteListException, AuthorizationError
from spapi.lock import RedisLock

s = requests.Session()


class Client(object):
    @property
    def headers(self):
        return {}

    @property
    def data(self):
        return {}

    @property
    def auth(self):
        return {}

    def get_url(self):
        return None

    def __init__(self, credentials, max_retries=3, is_grantless=False, region=None, redis_config=None):
        """
        is_grantless 是否无授权，默认为 False，即需要授权
        """
        self.region = region
        self.max_retries = max_retries
        self.credentials = credentials
        self.cred = CredentialProvider(credentials=credentials).credentials
        self._validate_client()
        self.is_grantless = is_grantless
        self.redis_lock = RedisLock([redis_config])

    def _validate_client(self):
        """client id 白名单限制"""
        client_id = self.cred.lwa_app_id
        if client_id not in ['amzn1.application-oa2-client.17141765d0ae41f18902c9bcc35591dd']:
            raise SPAPIClientIdNotInWhiteListException({'client_id': client_id})

    def _merge_headers(self, url, kwargs):
        url_parsed = urlparse(url)
        headers = self.headers
        headers['host'] = url_parsed.netloc
        if kwargs.get('headers'):
            headers.update(kwargs['headers'])
        return headers

    def _merge_data(self, kwargs):
        data = self.data
        if kwargs.get('data'):
            data.update(kwargs['data'])
        if data:
            return json.dumps(data)
        return data

    def request(self, method, url=None, **kwargs):
        if not url:
            url = self.get_url()

        if kwargs.get('region'):
            self.region = kwargs.pop('region')

        kwargs['auth'] = self.auth
        kwargs['headers'] = self._merge_headers(url, kwargs)
        kwargs['data'] = self._merge_data(kwargs)

        print('===================request===================', method, url, kwargs, '\n')
        response = s.request(method, url, **kwargs)
        print('===================response===================', response.status_code, response.text, '\n')
        return response

    def get_headers(self, url, **kwargs):
        return self._merge_headers(url, kwargs)

    def get_data(self, **kwargs):
        return self._merge_data(kwargs)


class RefreshTokenClient(Client):
    """根据RefreshToken刷新访问令牌
        POST /auth/o2/token HTTP/l.l
        Host: api.amazon.com
        Content-Type: application/x-www-form-urlencoded;charset=UTF-8
        grant_type=refresh_token
        &refresh_token=Aztr|...
        &client_id=foodev
        &client_secret=Y76SDl2F
    """

    URL = 'https://api.amazon.com/auth/o2/token'

    @property
    def auth(self):
        return {}

    @property
    def data(self):
        return {
            'grant_type': 'refresh_token',
            'client_id': self.cred.lwa_app_id,
            'client_secret': self.cred.lwa_client_secret,
            'refresh_token': self.cred.refresh_token,
        }

    @property
    def headers(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

    def _merge_data(self, kwargs):
        data = self.data
        if kwargs.get('data'):
            data.update(kwargs['data'])
        return data

    def get_url(self, **kwargs):
        return self.URL

    @staticmethod
    def check_response(resp):
        response_data = resp.json()
        if resp.status_code != 200:
            error_message = response_data.get('error_description')
            error_code = response_data.get('error')
            raise AuthorizationError(error_code, error_message, resp.status_code)
        return response_data


class GrantlessOperationClient(RefreshTokenClient):
    """调用无授权操作
        POST /auth/o2/token HTTP/l.l
        Host: api.amazon.com
        Content-Type: application/x-www-form-urlencoded;charset=UTF-8
        grant_type=client_credentials
        &scope=sellingpartnerapi::notifications
        &client_id=foodev
        &client_secret=Y76SDl2F
    """

    @property
    def data(self):
        return {
            'grant_type': 'client_credentials',
            'scope': 'sellingpartnerapi::notifications',  # TODO `sellingpartnerapi::migration`
            'client_id': self.cred.lwa_app_id,
            'client_secret': self.cred.lwa_client_secret,
        }


class AmazonSpApi(Client):
    SCHEMA = 'https://'
    CONTENT_TYPE = 'application/json'

    @property
    def headers(self):
        return {
            'x-amz-access-token': self.access_token,
            'x-amz-date': datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'),
        }

    @property
    def data(self):
        return {}

    @property
    def auth(self):
        """签名和授权"""

        role = self.role
        return AWSSigV4(
            'execute-api',
            aws_access_key_id=role.get('AccessKeyId'),
            aws_secret_access_key=role.get('SecretAccessKey'),
            region=self.region,
            aws_session_token=role.get('SessionToken')
        )

    @property
    def role(self):
        print('--------->>> def role')
        return self._lock_get_data('role_', self._get_role, 3000)

    @property
    def access_token(self):
        print('--------->>> def access_token')
        if not self.is_grantless:
            token = self._lock_get_data('token_', self._get_token, 3000)
        else:
            token = self._lock_get_data('grantless_token_', self._get_token, 3000)
        return token['access_token']

    def __init__(self, credentials, is_grantless=False, region=None):
        super(AmazonSpApi, self).__init__(credentials, is_grantless=is_grantless, region=region)
        self.boto3_client = boto3.client(
            'sts',
            aws_access_key_id=self.cred.aws_access_key,
            aws_secret_access_key=self.cred.aws_secret_key
        )
        self.is_grantless = is_grantless

    def _get_role(self):
        """角色代入"""

        role = self.boto3_client.assume_role(
            RoleArn=self.cred.role_arn,
            RoleSessionName=str(uuid.uuid4())
        )['Credentials']
        del role['Expiration']
        return role

    def _get_token(self):
        if not self.is_grantless:
            tsc = RefreshTokenClient(credentials=self.credentials)
        else:
            tsc = GrantlessOperationClient(credentials=self.credentials)
        resp = tsc.request('POST')
        return tsc.check_response(resp)

    def _lock_get_data(self, key_prefix, func, data_ttl, lock_ttl=1000 * 60 * 10):
        """Redis分布式锁，当前使用场景：
            1、刷新Token
            2、角色代入(assume role)
        """

        data_key = key_prefix + self.cred.refresh_token
        lock_key = key_prefix + '_lock_' + self.cred.refresh_token

        while True:
            data = cache.get(data_key)
            if not data:
                locked = self.redis_lock.lock(lock_key, lock_ttl)
                if locked:
                    try:
                        data = func()
                        print('--------->>> _lock_get_data->data = func()::', data)
                        cache.setex(data_key, data_ttl, json.dumps(data))
                    finally:
                        self.redis_lock.unlock(locked)
                    return data
            else:
                return json.loads(data)

            print('===================拿不到锁，先睡会儿===================', key_prefix, data)
            time.sleep(0.5)

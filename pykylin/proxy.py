from __future__ import absolute_import

import requests
from requests.auth import HTTPBasicAuth

from .encoding import decode
from .errors import Error
from .log import logger

class Proxy(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.cookies = {}
        self.user = None
        self.password = None
        self.auth = None
        self.headers = {'Content-Type': 'application/json;charset=UTF-8'}

    def login(self, user, password):
        route = 'user/authentication'
        url = '%s/%s' % (self.base_url, route)
        self.user = user
        self.password = user
        self.auth = HTTPBasicAuth(user, password)
        resp = requests.post(url, auth=self.auth, headers=self.headers)

        if resp.status_code != 200:
            raise Error('Login failed with username: "%s"' % self.user)
        else:
            logger.info('Login success with username: "%s"' % self.user)
            logger.debug('Authority details: %s', resp.text)

        jsesion_guid = resp.cookies['JSESSIONID']
        self.set_cookie('JSESSIONID', jsesion_guid)

    def request(self, method, route, **kwargs):
        url = '%s/%s' % (self.base_url, route)
        resp = requests.request(method, url, headers=self.headers, cookies=self.cookies, auth=self.auth, **kwargs)

        if resp.status_code != 200:
            exception = 'Unknown'
            try:
                err = decode(resp.text)
                exception = err['exception']
            except ValueError:
                pass
            finally:
                raise Error('Error when requesting: "%s", exception: "%s"' % (route, exception))

        return decode(resp.text)

    def post(self, route, **kwargs):
        return self.request('post', route, **kwargs)

    def get(self, route, **kwargs):
        return self.request('get', route, **kwargs)

    def set_cookie(self, cookie_key, cookie_value):
        self.cookies[cookie_key] = cookie_value

    def clear_cookie(self):
        self.cookies.clear()

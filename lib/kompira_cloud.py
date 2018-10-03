# coding: UTF-8

import requests
import urllib.parse

class KompiraCloudAPI(object):

    def __init__(self, token, username=None, password=None):
        self.token = token
        self.timeout = 10
        self.request_header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Authorization': 'Token %s' % self.token,
        }
        if username is not None:
            self.auth = requests.auth.HTTPBasicAuth(username, password)
        else:
            self.auth = None

    def get(self, url, params={}):
        try:
            res = requests.get(url, params=params, headers=self.request_header, auth=self.auth, timeout=self.timeout)
            if res.status_code != 200:
                raise requests.RequestException(res.text)
            res = res.json()
        except requests.RequestException as e:
            # logging?
            raise
        except ValueError as e:
            # logging?
            raise
        return res

    def convert_api_url(self, url):
        uri = urllib.parse.urlparse(url)
        if uri.path.startswith('/api'):
            return url
        return uri._replace(path = '/api' + uri.path).geturl()

    def get_from_url(self, url, params={}):
        url = self.convert_api_url(url)
        return self.get(url, params)

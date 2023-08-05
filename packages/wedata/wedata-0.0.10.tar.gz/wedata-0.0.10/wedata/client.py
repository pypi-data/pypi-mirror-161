import json
import threading

import requests
import pandas as pd

from .config import Config
from .checker import Checker


class BaseClient(object):
    _threading_local = threading.local()

    def __init__(self):
        self.host = Config.host
        self.port = Config.port
        self._refresh_token = None
        self._access_token = None
        self._instance = None
        self.root_url = f'http://{self.host}:{self.port}/api/v1'

    @classmethod
    def instance(cls):
        _instance = getattr(cls._threading_local, '_instance', None)
        if _instance is None:
            _instance = Client()
            cls._threading_local._instance = _instance
        return _instance

    def _post_with_token(self, url, param):
        headers = {
            "Authorization": f'Bearer {self._access_token}'
        }
        r = requests.post(url, json=param, headers=headers)
        return r

    def _login(self, username, password, refresh=True):
        url = f'{self.root_url}/security/login'
        if refresh:
            body = {
                "username": username,
                "password": password,
                "provider": 'db',
                "refresh": True
            }
        else:
            body = {
                "username": username,
                "password": password,
                "provider": 'db'
            }
        headers = {
            "Content-Type": "application/json"
        }
        r = requests.post(url, data=json.dumps(body), headers=headers)
        return r

    def _refresh(self, refresh_token):
        url = f"{self.root_url}/security/refresh"
        headers = {
            "Authorization": f'Bearer {refresh_token}'
        }
        r = requests.post(url, headers=headers)
        return r

    def login(self, username, password):
        try:
            r = self._login(username, password, refresh=False)
        except Exception as e:
            raise Exception(f"网络连接失败")
        if r.status_code == 200:
            # login succeed
            result = r.json()
            self._access_token = result['access_token']
        elif r.status_code == 401:
            result = r.json()
            raise Exception(f"登陆失败, 返回码: {r.status_code}, 返回值:{result['message']}")
        else:
            raise Exception(f"Connection failed")

    def post_with_token(self, url, param) -> pd.DataFrame:
        if self._access_token is None:
            raise Exception("Login required")
        try:
            r = self._post_with_token(url, param)
        except Exception as e:
            raise Exception(f"网络连接失败")
        if r.status_code == 200:
            # login succeed
            result = r.json()
            return result
        elif r.status_code == 401:
            result = r.json()
            raise Exception(f"登陆失败, 返回码: {r.status_code}, 返回信息: {result['message']}")
        elif r.status_code == 400:
            result = r.json()
            raise Exception(f"参数错误, 返回码: {r.status_code}, 返回信息: {result['message']}")
        elif r.status_code == 500:
            raise Exception(f"未知错误, 请联系管理员")
        else:
            raise Exception(f"网络连接失败")


class Client(BaseClient):

    def __init__(self):
        super(Client, self).__init__()

    def query_sheet(self, param) -> pd.DataFrame:
        q = {k: v for k, v in param.items() if k not in ["domain", "phylum", "class"]}
        url = f'{self.root_url}/{param.get("domain")}/{param.get("phylum")}/{param.get("class")}'
        result = self.post_with_token(url, q)
        d = pd.DataFrame.from_records(result['data'])
        return d

    def query_descriptor(self, param) -> pd.DataFrame:
        url = f'{self.root_url}/{param.get("domain")}/{param.get("phylum")}/{param.get("class")}'
        result = self.post_with_token(url, param)
        d = pd.DataFrame.from_records(result['data'])
        return d

    def query(self, param) -> pd.DataFrame:
        if param["domain"] == "sheet":
            res = self.query_sheet(param)
        elif param["domain"] == "descriptor":
            res = self.query_descriptor(param)
        else:
            raise Exception("Params error, invalid domain")
        return res

    def extract_sheet(self, param) -> dict:
        url = f'{self.root_url}/{param.get("domain")}/{param.get("phylum")}/extract'
        q = param
        result = self.post_with_token(url, q)
        df = pd.DataFrame.from_records(result['data'])
        res = {key: group for key, group in df.groupby('TRADE_DT')}
        return res

    def extract_descriptor(self, param) -> dict:
        df = self.query_descriptor(param)
        if df.empty:
            return {}
        res = {key: group for key, group in df.groupby('date')}
        return res

    def extract(self, param):
        if param["domain"] == "sheet":
            res = self.extract_sheet(param)
        elif param["domain"] == "descriptor":
            res = self.extract_descriptor(param)
        else:
            raise Exception("Params error, invalid domain")
        return res

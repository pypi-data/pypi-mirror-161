from .client import Client
from .checker import Checker

__all__ = ['login', 'query', 'extract']


def login(username, password):
    """通过username和password登陆，设置token"""
    client = Client.instance()
    client.login(username, password)


def query(param):
    """查询接口"""
    client = Client.instance()
    Checker.check_params(param)
    d = client.query(param)
    return d


def extract(param):
    """提取接口"""
    client = Client.instance()
    Checker.check_params(param)
    d = client.extract(param)
    return d

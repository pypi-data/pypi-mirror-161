import sys
import os

from wedata.client import Client


class TestClient:
    def setup_class(self):
        client = Client()
        client.login('admin', 'admin')
        self.client = client

    def test_query_sheet(self):
        param = {
            'domain': 'sheet',
            'phylum': 'trading',
            'class': 'asharecalendar',
            'fields': ['TRADE_DAYS', 'S_INFO_EXCHMARKET'],
            'start_date': '20180101',
            'end_date': '20221231',
            'codes': ['000300.SH']
        }
        self.client.query(param)

    def test_extract_sheet(self):
        param = {
            'domain': 'sheet',
            'phylum': 'direct',
            'class': 'asharefinancialindicator_S_FA_INTERESTDEBT',
            'fields': [],
            'start_date': '20180101',
            'end_date': '20181231',
            'codes': ['000300.SH']
        }
        param["class"] = param["class"].lower()
        self.client.extract(param)

    def test_query_descriptor(self):
        param = {
            'case': 'case001',
            'user': 'uid001',
            'domain': 'descriptor',
            'phylum': 'characteristic',
            'class': 'characteristic_exposure',
            'fields': [],
            'start_date': '20210101',
            'end_date': '20210102',
            'codes': [],
        }
        param["class"] = param["class"].lower()
        res = self.client.query(param)
        print(res)

    def test_extract_descriptor(self):
        param = {
            'case': 'case001',
            'user': 'uid001',
            'domain': 'descriptor',
            'phylum': 'characteristic',
            'class': 'characteristic_exposure',
            'fields': [],
            'start_date': '20210101',
            'end_date': '20210102',
            'codes': [],
        }
        param["class"] = param["class"].lower()
        res = self.client.extract(param)
        print(res)


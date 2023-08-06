import json

import os
import requests

from client.TradingInterface.TradingInterface import TradingInterface

BASE_URL = "https://masterswift-beta.mastertrust.co.in/api/v1"

ROUTE_LOGIN = "/user/login"

ROUTE_ORDER = "/orders/"

ROUTE_TWOFA = "/user/twofa"

ROUTE_POSITION = "/positions"

TRUINVEST_DEV = "https://devapi.truinvest.ai"

TRUINVEST_PROD = "https://api.truinvest.ai"

TRUINVEST_ROUTE_INSTRUMENTS = "trade/instrument_mapping/?truinvest_secret={}"

TRUINVEST_ROUTE_MARGIN = "user/fetch-margin?broker={}&api_key={}&truinvest_secret={}"


class MasterTrustBroker(TradingInterface):
    def __init__(self, login_id, password, truinvest_secret: str):
        self.login_id = login_id
        self.password = password
        self.two_fa_token = None
        self.access_token = None
        self.margin = 0
        self.truinvest_secret = truinvest_secret
        self.instrument_token_lookup = dict()
        self.GetInstruments()

    def Login(self):
        payload = {
            "login_id": self.login_id,
            "password": self.password,
            "device": "WEB"
        }
        headers = {
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }
        response = requests.request("POST", BASE_URL + ROUTE_LOGIN, headers=headers, json=payload)
        if response.status_code == 200:
            res = response.json()
            print(res)
            self.two_fa_token = res['data']['twofa_token']
            return True
        return False

    def PlaceOrder(self, qty: int, transaction_type: str, trading_symbol: str, exchange: str, product_type: str):
        headers = {
            'X-Authorization-Token': self.access_token,
            'X-Device-Type': "web",
            'Content-Type': 'application/json'
        }
        payload = {
            "exchange": exchange.upper(),
            "order_type": "MARKET",
            "instrument_token": self.instrument_token_lookup[trading_symbol]['instrument_token'],
            "quantity": qty,
            "disclosed_quantity": 0,
            "order_side": transaction_type.upper(),
            "validity": "DAY",
            "product": product_type.upper(),
            "client_id": self.login_id,
            "user_order_id": 10000,
            "market_protection_percentage": 5,
            "device": "WEB"
        }
        response = requests.request("POST", BASE_URL + ROUTE_ORDER, headers=headers, data=json.dumps(payload))
        print(response.json())

    def Margins(self):
        base_url = TRUINVEST_DEV
        if os.environ.get('env') == 'prod':
            base_url = TRUINVEST_PROD
        route = TRUINVEST_ROUTE_MARGIN.format("MASTERTRUST", self.login_id, self.truinvest_secret)
        url = f"{base_url}/{route}"
        response = requests.request("GET", url)

        return {
            "collateral": response.json()['collateral'],
            "cash": response.json()['cash']
        }

    def Positions(self) -> list:
        querystring = {"type": "historical", "client_id": self.login_id}

        headers = {
            'X-Authorization-Token': self.access_token,
            'X-Device-Type': "web"
        }

        response = requests.request("GET", BASE_URL + ROUTE_POSITION, headers=headers, params=querystring)

        positions = []
        for position in response.json()['data']:
            positions.append({'symbol_id': position['instrument_token'],
                              'tradingsymbol': position['trading_symbol'],
                              'quantity': position['net_quantity'],
                              'pnl': 0,
                              'buy_quantity': position['buy_quantity'],
                              'sell_quantity': position['sell_quantity']})

        return positions

    def GenerateSession(self, mPin: str):
        payload = {
            "login_id": self.login_id,
            "twofa": [
                {
                    "question_id": 1,
                    "answer": mPin
                }
            ],
            "twofa_token": self.two_fa_token
        }
        headers = {
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }
        response = requests.request("POST", BASE_URL + ROUTE_TWOFA, headers=headers, json=payload)
        if response.status_code == 200:
            res = response.json()
            self.access_token = res['data']['auth_token']
            print(res)

    def GetInstruments(self):
        base_url = TRUINVEST_DEV
        if os.environ.get('env') == 'prod':
            base_url = TRUINVEST_PROD
        route = TRUINVEST_ROUTE_INSTRUMENTS.format(self.truinvest_secret)
        url = f"{base_url}/{route}"
        response = requests.request("GET", url)
        instruments = []
        if response.status_code == 200:
            instruments = response.json()

        for instrument in instruments:
            self.instrument_token_lookup[instrument['trading_symbol']] = {
                                            'instrument_token': instrument['token'],
                                            # 'lot_size': instrument['lot_size']
            }

    def Holdings(self):
        super().Holdings()

    def GetQuote(self, listInstruments, exchange):
        super().GetQuote(listInstruments, exchange)

    def Orders(self):
        super().Orders()

    def Profile(self):
        super().Profile()

    def GetAvailableMargin(self):
        margin = self.Margins()
        data = {'adhoc_margin': 0,
                'cash': margin['cash'],
                'opening_balance': margin['cash'],
                'live_balance': margin['cash'],
                'collateral': margin['collateral'],
                'intraday_payin': 0}
        return data

    def GetUtilizedMargin(self):
        pass

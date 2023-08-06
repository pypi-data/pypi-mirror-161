from client.TradingInterface.TradingInterface import TradingInterface
import requests
import json

BASE_URL = "https://14.97.57.98:44551/api"
ROUTE_LOGIN = "/accounts/login/"
ROUTE_ORDER = "/orders/"
ROUTE_MARGIN = ROUTE_ORDER + "margin/"
ROUTE_POSITIONS = ROUTE_ORDER + "positions/"
ROUTE_TRADES = ROUTE_ORDER + "trades/"
ROUTE_HOLDINGS = ROUTE_ORDER + "holdings/"
ROUTE_MPIN = "/accounts/mpin/"


def refreshAccessToken(refresh_token) -> str:
    return "access_token"


def getSymbolId(trading_symbol):
    # TODO: Refresh SYMBOL IDs cron day - 7AM

    pass


class UTradeBroker(TradingInterface):
    def __init__(self, username, password, baseUrl=BASE_URL):
        self.username = username
        self.password = password
        self.token = ""
        self.base_url = baseUrl
        self.login_token = ""
        self.access_token = ""
        self.refresh_token = ""

    def Login(self) -> str:
        payload = json.dumps({
            "username": self.username,
            "password": self.password,
            "platform": "web"
        })
        headers = {
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }
        response = requests.request("POST", self.base_url + ROUTE_LOGIN, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            res = response.json()
            print(res)
            self.login_token = res['two_factor_token']
            return "logged_in"
        return "login_failed"

    def PlaceOrder(self, qty, transaction_type: str, trading_symbol, exchange, product_type):
        #         TODO: Add refresh Access Token Code
        # smy_id = getSymbolId(trading_symbol)
        # self.access_token = refreshAccessToken(self.refresh_token)
        payload = json.dumps({
            "side": transaction_type.lower(),
            "product_type": "Delivery",
            "symbol_id": trading_symbol,
            "order_type": "market",
            "quantity": qty,
            "disclosed_qty": 0,
            "disclosed": "0",
            "square_off": 0,
            "validity": "day"
        })
        headers = {
            'Authorization': 'Token ' + self.access_token,
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }

        response = requests.request("POST", self.base_url + ROUTE_ORDER, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            print("Request Data->")
            print(payload)
            print(response.json())
        else:
            print("Order Not Placed->", response.json())

    def Margins(self):
        headers = {
            'Authorization': 'Token ' + self.access_token,
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }
        print("Url->{}".format(self.base_url + ROUTE_MARGIN))
        print("headers->{}".format(headers))
        response = requests.request("GET", self.base_url + ROUTE_MARGIN, headers=headers, verify=False)
        if response.status_code == 200:
            print(response.json())
            data = {
                "net_bal": response.json()['net_mtm'],
                "cash_available": response.json()['cash_available']
            }
        else:
            print("Error in Fetching margin->", response.json())
            data = {
                "net_bal": 0,
                "cash_available": 0
            }
        return data

    def Positions(self):
        headers = {
            'Authorization': 'Token ' + self.access_token,
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }
        print("Url-->", self.base_url + ROUTE_POSITIONS)
        print("Headers->", headers)
        response = requests.request("GET", self.base_url + ROUTE_POSITIONS, headers=headers, verify=False)
        print("I am here")
        position = list()
        if response.status_code == 200:
            # print(response.json())
            # TODO: Preprocessing Required
            for pos in response.json()['data']:
                position.append({'symbol_id': pos['symbol_id'],
                                 'tradingsymbol': pos['symbol_id'],
                                 'quantity': pos['buy_qty'] - pos['sell_qty'],
                                 'pnl': pos['net_profit_loss'],
                                 'buy_quantity': pos['buy_qty'],
                                 'sell_quantity': pos['sell_qty']})
            return position
        else:
            print("Error in Fetching margin->", response.json())
            return []

    def GenerateSession(self, mPin=123456) -> bool:
        payload = json.dumps({
            "pin": mPin,
            "token": self.login_token,
            "username": self.username,
            "platform": "web"
        })
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", self.base_url + ROUTE_MPIN, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            res = response.json()
            print(res['access_token'])
            self.access_token = res['access_token']
            self.refresh_token = res['refresh_token']
            return True
        return False

    def GetInstruments(self):
        super().GetInstruments()

    def Holdings(self):
        headers = {
            'Authorization': 'Token ' + self.access_token,
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }
        print("Url->", self.base_url + ROUTE_HOLDINGS)
        print("Headers->", headers)
        response = requests.request("GET", self.base_url + ROUTE_HOLDINGS, headers=headers, verify=False)
        if response.status_code == 200:
            # print(response.json())
            # TODO: Preprocessing Required
            return response.json()
        else:
            print("Error in Fetching margin->", response.json())
            return []

    def GetQuote(self, listInstruments, exchange):
        super().GetQuote(listInstruments, exchange)

    def Orders(self):
        super().Orders()

    def Profile(self):
        super().Profile()

    def GetAvailableMargin(self):
        headers = {
            'Authorization': 'Token ' + self.access_token,
            'Content-Type': 'application/json',
            'App-Secret': '1'
        }
        print("Url->{}".format(self.base_url + ROUTE_MARGIN))
        print("headers->{}".format(headers))
        response = requests.request("GET", self.base_url + ROUTE_MARGIN, headers=headers, verify=False)
        if response.status_code == 200:
            print(response.json())
            data = {'adhoc_margin': response.json()['adhoc'],
                    'cash': response.json()['cash'],
                    'opening_balance': response.json()['cash'],
                    'live_balance': response.json()['cash'],
                    'collateral': response.json()['collateral'],
                    'intraday_payin': response.json()['pay_in']}
            return data
        else:
            return {'adhoc_margin': 0,
                    'cash': 0,
                    'opening_balance': 0,
                    'live_balance': 0,
                    'collateral': 0,
                    'intraday_payin': 0}

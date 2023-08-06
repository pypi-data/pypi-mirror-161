from ks_api_client import ks_api
from client.TradingInterface.TradingInterface import TradingInterface


class KotakTrading(TradingInterface):
    def __init__(self, api_key: str, api_secret: str, request_token: str, access_token: str,
                 is_session_generated: bool, oauth_code: str):
        self.userId = api_key
        self.password = api_secret
        self.access_token = access_token
        self.consumer_key = request_token
        self.oauth_code = oauth_code
        self.kotak_obj = ks_api.KSTradeApi(access_token=self.access_token, userid=self.userId,
                                           ip="", app_id="", consumer_key=self.consumer_key,
                                           host="https://sbx.kotaksecurities.com/apim")

    def Login(self):
        data = self.kotak_obj.login(password=self.password)
        if 'Success' in data.keys():
            return 'Success'
        else:
            return 'Failed'

    def PlaceOrder(self, qty, transaction_type, trading_symbol, exchange, product_type):
        super().PlaceOrder(qty, transaction_type, trading_symbol, exchange, product_type)

    def Margins(self):
        super().Margins()

    def Positions(self):
        super().Positions()

    def GenerateSession(self, mPin):
        self.kotak_obj.session_2fa(access_code=self.access_token)

    def GetInstruments(self):
        super().GetInstruments()

    def GetHoldings(self):
        pass

    def GetQuote(self, listInstruments, exchange):
        pass

    def GetOrders(self):
        pass

    def GetProfile(self):
        pass

    def GetQuoteNSE(self):
        pass

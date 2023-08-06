from client.TradingInterface.TradingInterface import TradingInterface

from client.KiteTrading.KiteTrading import KiteTrading
from client.uTradeBroker.uTradeBroker import UTradeBroker
from client.MasterTrust.MasterTrust import MasterTrustBroker

BROKER_KITE = "KITE"
BROKER_KOTAK = "KOTAK"
BROKER_ICICI = "ICICI"
BROKER_UTRADE = "uTrade"
BROKER_MASTER_TRUST = "MasterTrustBroker"

EXCHANGE_NSE = "NSE"
EXCHANGE_BSE = "BSE"
EXCHANGE_NFO = "NFO"
EXCHANGE_CDS = "CDS"
EXCHANGE_BFO = "BFO"
EXCHANGE_MCX = "MCX"

PRODUCT_MIS = "MIS"
PRODUCT_CNC = "CNC"
PRODUCT_NRML = "NRML"
PRODUCT_CO = "CO"
PRODUCT_BO = "BO"


class TruinvestBroker(TradingInterface):

    def __init__(self, api_key, api_secret, broker, truinvest_secret, is_session_generated=True,
                 access_token: str = "", request_token: str = "", mPin: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.request_token = request_token
        self.access_token = access_token
        self.broker_name = broker
        self.broker_obj = None
        if self.broker_name == BROKER_KITE:
            self.broker_obj = KiteTrading(self.api_key, self.api_secret, self.request_token,
                                                      self.access_token, is_session_generated,
                                                      truinvest_secret=truinvest_secret)
        elif self.broker_name == BROKER_KOTAK:
            self.broker_obj = None
        elif self.broker_name == BROKER_ICICI:
            self.broker_obj = None
        elif self.broker_name == BROKER_UTRADE:
            self.broker_obj = UTradeBroker(username=self.api_key, password=self.api_secret)
        elif self.broker_name == BROKER_MASTER_TRUST:
            self.broker_obj = MasterTrustBroker(login_id=api_key, password=api_secret,
                                                            truinvest_secret=truinvest_secret)
            self.broker_obj.Login()
        if not is_session_generated:
            self.broker_obj.GenerateSession(mPin=mPin)

    def Login(self) -> str:
        return self.broker_obj.Login()

    def GetTradingClientObj(self):
        return self.broker_obj.GenerateSession()

    def PlaceOrder(self, qty, transaction_type, trading_symbol, exchange, product_type):
        return self.broker_obj.PlaceOrder(qty, transaction_type, trading_symbol, exchange, product_type)

    def Margins(self):
        return self.broker_obj.Margins()

    def Positions(self):
        return self.broker_obj.Positions()

    def Holdings(self):
        return self.broker_obj.Holdings()

    def Orders(self):
        return self.broker_obj.Orders()

    def Profile(self):
        return self.broker_obj.Profile()

    def GenerateSession(self, mPin="123456"):
        return self.broker_obj.GenerateSession(mPin=mPin)

    def GetInstruments(self):
        return self.broker_obj.GetInstruments()

    def GetQuote(self, listInstruments, exchange):
        return self.broker_obj.GetQuote(listInstruments, exchange)

    def GetAvailableMargin(self):
        return self.broker_obj.GetAvailableMargin()

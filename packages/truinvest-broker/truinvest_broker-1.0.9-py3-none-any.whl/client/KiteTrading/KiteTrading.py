from kiteconnect import KiteConnect, exceptions
from rest_framework import status
from client.TradingInterface.TradingInterface import TradingInterface


def modPositions(positions):
    req_col = ['tradingsymbol', 'pnl', 'quantity', 'buy_quantity', 'sell_quantity']
    mod_positions = list()
    mod_positions.append(req_col)
    for position in positions:
        pos = {}
        for key, value in position.items():
            if key in req_col:
                pos[key] = value
        mod_positions.append(pos)
    return mod_positions


class KiteTrading(TradingInterface):
    def __init__(self, api_key: str, api_secret: str, request_token: str, access_token: str,
                 is_session_generated: bool, truinvest_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.request_token = request_token
        self.access_token = access_token
        self.kite = KiteConnect(api_key=self.api_key)
        if is_session_generated:
            self.kite.set_access_token(self.access_token)

    def Login(self):
        return self.kite.login_url()

    def GenerateSession(self, mPin: str):
        data = {}
        # user_data
        try:
            data['status'] = status.HTTP_201_CREATED
            user_data = self.kite.generate_session(self.request_token, api_secret=self.api_secret)
            print(user_data)
            data['user'] = user_data
            self.kite.set_access_token(user_data['access_token'])
            self.access_token = user_data['access_token']
        except exceptions.TokenException as exp:
            print('Error-{}'.format(exp))
            data['status'] = status.HTTP_403_FORBIDDEN
            # data['user'] = self.connectKite()
            # data['error'] = exp
        return data

    def PlaceOrder(self, qty, transaction_type, trading_symbol, exchange, product_type):
        try:
            print("order {}-{}-{}".format(trading_symbol, qty, transaction_type, self.kite.PRODUCT_CNC))
            # entryTrade = 0
            entryTrade = self.kite.place_order(tradingsymbol=trading_symbol,
                                               exchange=exchange,
                                               transaction_type=transaction_type,
                                               quantity=qty,
                                               order_type=self.kite.ORDER_TYPE_MARKET,
                                               product=product_type,
                                               variety=self.kite.VARIETY_REGULAR
                                               )
        except Exception as E:
            print("Order Not Placed")
            print("trading_symbol-{}".format(trading_symbol))
            print("transaction_type-{}".format(transaction_type))
            print("Qty-{}".format(qty))
            print("Error-{}".format(E))
            entryTrade = 0
        return entryTrade

    def Margins(self):
        data = dict()
        try:
            data['status'] = status.HTTP_200_OK
            margins = self.kite.margins()
            print(margins)
            net_bal = margins['equity']['net']
            cash_bal = margins['equity']['available']['cash']
            data['user'] = (net_bal, cash_bal)
        except Exception as e:
            data['status'] = status.HTTP_401_UNAUTHORIZED
            print("Error-{}".format(e))
            # data['user'] = self.kite.connectKite()
        return data

    def Positions(self):
        pos_net = modPositions(self.kite.positions()['net'])
        pos_day = modPositions(self.kite.positions()['day'])
        return pos_net, pos_day

    def GetInstruments(self):
        return self.kite.instruments()

    def GetHoldings(self):
        data = {
            'holdings': self.kite.holdings(),
            'mf_holdings': self.kite.mf_holdings()
        }
        return data

    def GetQuote(self, listInstruments, exchange):
        if exchange == "NSE":
            for i in range(len(listInstruments)):
                listInstruments[i] = 'NSE:' + listInstruments[i]
        elif exchange == "NFO":
            for i in range(len(listInstruments)):
                listInstruments[i] = 'NFO:' + listInstruments[i]
        return self.kite.quote(listInstruments)

    def Orders(self):
        return self.kite.orders()

    def Profile(self):
        return self.kite.profile()

    def GetAvailableMargin(self):
        return self.kite.margins()['equity']['available']

    def GetUtilizedMargin(self):
        return self.kite.margins()['equity']['Utilized']

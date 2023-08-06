class TradingInterface:
    def Login(self):
        pass

    def PlaceOrder(self, qty, transaction_type, trading_symbol, exchange, product_type):
        pass

    def Margins(self):
        pass

    def Positions(self):
        pass

    def GenerateSession(self, mPin):
        pass

    def GetInstruments(self):
        pass

    def Holdings(self):
        pass

    def GetQuote(self, listInstruments, exchange):
        pass

    def Orders(self):
        pass

    def Profile(self):
        pass

    def GetAvailableMargin(self):
        pass

    def GetUtilizedMargin(self):
        pass

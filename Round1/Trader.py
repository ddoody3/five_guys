import json
from typing import Dict, List
from json import JSONEncoder
import jsonpickle
import string

Time = int
Symbol = str
Product = str
Position = int
UserId = str
ObservationValue = int

class Listing:
    def __init__(self, symbol: Symbol, product: Product, denomination: Product):
        self.symbol = symbol
        self.product = product
        self.denomination = denomination


class ConversionObservation:
    def __init__(
        self,
        bidPrice: float,
        askPrice: float,
        transportFees: float,
        exportTariff: float,
        importTariff: float,
        sunlight: float,
        humidity: float,
    ):
        self.bidPrice = bidPrice
        self.askPrice = askPrice
        self.transportFees = transportFees
        self.exportTariff = exportTariff
        self.importTariff = importTariff
        self.sunlight = sunlight
        self.humidity = humidity

class Observation:
    def __init__(
        self,
        plainValueObservations: Dict[Product, ObservationValue],
        conversionObservations: Dict[Product, ConversionObservation],
    ) -> None:
        self.plainValueObservations = plainValueObservations
        self.conversionObservations = conversionObservations

    def __str__(self) -> str:
        return (
            "(plainValueObservations: "
            + jsonpickle.encode(self.plainValueObservations)
            + ", conversionObservations: "
            + jsonpickle.encode(self.conversionObservations)
            + ")"
        )

class Order:
    def __init__(self, symbol: Symbol, price: int, quantity: int) -> None:
        self.symbol = symbol
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"

    def __repr__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"


class OrderDepth:
    def __init__(self):
        self.buy_orders: Dict[int, int] = {}
        self.sell_orders: Dict[int, int] = {}

class Trade:
    def __init__(
        self,
        symbol: Symbol,
        price: int,
        quantity: int,
        buyer: UserId = None,
        seller: UserId = None,
        timestamp: int = 0,
    ) -> None:
        self.symbol = symbol
        self.price: int = price
        self.quantity: int = quantity
        self.buyer = buyer
        self.seller = seller
        self.timestamp = timestamp

    def __str__(self) -> str:
        return (
            "("
            + self.symbol
            + ", "
            + self.buyer
            + " << "
            + self.seller
            + ", "
            + str(self.price)
            + ", "
            + str(self.quantity)
            + ", "
            + str(self.timestamp)
            + ")"
        )

    def __repr__(self) -> str:
        return (
            "("
            + self.symbol
            + ", "
            + self.buyer
            + " << "
            + self.seller
            + ", "
            + str(self.price)
            + ", "
            + str(self.quantity)
            + ", "
            + str(self.timestamp)
            + ")"
        )

class TradingState(object):
    def __init__(
        self,
        traderData: str,
        timestamp: Time,
        listings: Dict[Symbol, Listing],
        order_depths: Dict[Symbol, OrderDepth],
        own_trades: Dict[Symbol, List[Trade]],
        market_trades: Dict[Symbol, List[Trade]],
        position: Dict[Product, Position],
        observations: Observation,
    ):
        self.traderData = traderData
        self.timestamp = timestamp
        self.listings = listings
        self.order_depths = order_depths
        self.own_trades = own_trades
        self.market_trades = market_trades
        self.position = position
        self.observations = observations

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class ProsperityEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class Trader:
    starfruit_cache = []
    POSITION_LIMIT = {'AMETHYSTS' : 20, 'STARFRUIT' : 20}
    starfruit_dim = 4
    def calc_next_price_starfruit(self):

            coef = [0.34172,0.261144,0.207718,0.188951]
            intercept = 2.355276
            nxt_price = intercept
            for i, val in enumerate(self.starfruit_cache):
                print(i)
                nxt_price += val * coef[i]

            return int(round(nxt_price))

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        for product in state.order_depths:
            try:
                maxorder = self.POSITION_LIMIT[product] - state.position[product]
            except: 
                maxorder = self.POSITION_LIMIT[product]
            if product == 'AMETHYSTS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                acceptable_price_amethysts = 10000  # Participant should calculate this value
                print("Acceptable price : " + str(acceptable_price_amethysts))
                print(
                    "Buy Order depth : "
                    + str(len(order_depth.buy_orders))
                    + ", Sell order depth : "
                    + str(len(order_depth.sell_orders))
                )

                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price_amethysts:
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
                        #orders.append(Order(product, best_ask, max(maxorder,-best_ask_amount)))

                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price_amethysts:
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        #orders.append(Order(product, best_bid, max(40-maxorder,-best_bid_amount)))
            
            elif product == 'STARFRUIT':
                order_depth: OrderDepth = state.order_depths[product]
                if len(self.starfruit_cache) == self.starfruit_dim:
                    self.starfruit_cache.pop(0)

                best_bid = list(order_depth.buy_orders.items())[0][0]
                best_ask = list(order_depth.sell_orders.items())[0][0]
                
                if len(self.starfruit_cache) == self.starfruit_dim:
                    self.starfruit_cache.append((best_bid+best_ask)/2)
            
                orders: List[Order] = []

                

                acceptable_price_starfruit = self.calc_next_price_starfruit() 

                #else: acceptable_price = 10000  # Participant should calculate this value
                print("Acceptable price : " + str(acceptable_price_starfruit))
                print(
                    "Buy Order depth : "
                    + str(len(order_depth.buy_orders))
                    + ", Sell order depth : "
                    + str(len(order_depth.sell_orders))
                )

                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < (acceptable_price_starfruit):
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
                        #orders.append(Order(product, best_ask, max(maxorder,-best_ask_amount)))

                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > (acceptable_price_starfruit):
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        #orders.append(Order(product, best_bid, max(40-maxorder,-best_bid_amount)))

            result[product] = orders

        # traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = state.traderData

        conversions = 1
        return result, conversions, traderData

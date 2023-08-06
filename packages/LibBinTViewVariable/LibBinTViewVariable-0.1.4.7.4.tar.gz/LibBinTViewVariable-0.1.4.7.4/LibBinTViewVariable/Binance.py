from dataclasses import dataclass
from enum import Enum, unique
from typing import List

from LibBinTViewVariable import Assets


@unique
class ModeBinanceListener(Enum):
    Futures = "binance.com-futures"
    DemoFutures = "binance.com-futures-testnet"


@unique
class ModeBinanceClient(Enum):
    Futures = "https://fapi.binance.com"
    DemoFutures = "https://testnet.binancefuture.com"


@dataclass
class AuthData:
    ApiKey: str
    ApiSecret: str
    Mode: ModeBinanceListener or ModeBinanceClient


@unique
class FUTURE_ORDER_TYPES(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP = 'STOP'
    STOP_MARKET = 'STOP_MARKET'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
    LIMIT_MAKER = 'LIMIT_MAKER'


@unique
class ORDER_STATUS(Enum):
    NEW = 'NEW'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    PENDING_CANCEL = 'PENDING_CANCEL'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'


@unique
class ORDER_TYPES(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_LOSS = 'STOP_LOSS'
    STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    LIMIT_MAKER = 'LIMIT_MAKER'


@unique
class SIDE(Enum):
    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'
@unique
class TypePosition(Enum):
    ShortMarket = '1'
    ShortLimit = '2'
    LongMarket= '3'
    LongLimit = '4'


@unique
class TIME_IN_FORCE(Enum):
    GTC = 'GTC'  # Good till cancelled
    IOC = 'IOC'  # Immediate or cancel
    FOK = 'FOK'  # Fill or kill


@dataclass
class TeikStop:
    Teik: float
    Stop: float
    Label: str


@dataclass
class Order:
    """
        id_stop_loss_order: номер (id) стоп-лосс ордера
        Id_take_profit_order: номер (id) стоп-лимита ордера
        cryptoPair: Пара надо из класса CryptoPair. Пример: CryptoPair.USDT_RUB
    """

    Label: str
    Profit: float
    EntryPrice: float
    FilledPrice: float
    Quantity: float
    StopLoss: float
    TeikProfit: float
    Id_stop_loss_order: int
    Id_take_profit_order: int
    UnixDataInput: int
    UnixDataOutput: int



@dataclass
class Position:
    Type:TypePosition
    Asset: Assets
    Name: str
    Orders: List[Order]


# {
# 'stream_type': 'ethusdt@kline_3m',
# 'event_type': 'kline',
# 'event_time': 1635593498687,
# 'symbol': 'ETHUSDT',
# 'kline':
#         {
#         'kline_start_time': 1635593400000,
#         'kline_close_time': 1635593579999,
#         'symbol': 'ETHUSDT',
#         'interval': '3m',
#         'first_trade_id': False,
#         'last_trade_id': False,
#         'open_price': '4337.52',
#         'close_price': '4334.05',
#         'high_price': '4337.61',
#         'low_price': '4332.67',
#         'base_volume': '153.744',
#         'number_of_trades': 45,
#         'is_closed': False,
#         'quote': '666513.06792',
#         'taker_by_base_asset_volume': '88.825',
#         'taker_by_quote_asset_volume': '385025.05646',
#         'ignore': '0'
#         },
# 'unicorn_fied': ['binance.com-futures', '0.11.0']
# }
@dataclass
class KlineData:
    Asset: str
    Kline: str
    EventTime: int
    Open: float
    Close: float
    High: float
    Low: float

# {
# 'stream_type':                'ORDER_TRADE_UPDATE',       'ORDER_TRADE_UPDATE',
# 'event_type':                 'ORDER_TRADE_UPDATE',       'ORDER_TRADE_UPDATE',
# 'event_time':                  1635393780938,             1635393515324
# 'symbol':                     'BTCUSDT',
# 'client_order_id':            'web_SxfDeGG1RKpckHjHiMyv',
# 'side':                       'BUY',
# 'order_type':                 'LIMIT',
# 'time_in_force':              'GTC',
# 'order_quantity':             '0.009',
# 'order_price':                '58917.69',
# 'order_avg_price':            '0',
# 'order_stop_price':           '0',
# 'current_execution_type':     'CANCELED',
# 'current_order_status':       'CANCELED',
# 'order_id':                   2855797558,
# 'last_executed_quantity':     '0',
# 'cumulative_filled_quantity': '0',
# 'last_executed_price':        '0',
# 'transaction_time':           1635393780936,
# 'trade_id':                   0,
# 'net_pay':                    '0',
# 'net_selling_order_value':    '0',
# 'is_trade_maker_side':        False,
# 'reduce_only':                False,
# 'trigger_price_type':         'CONTRACT_PRICE',
# 'order_price_type':           'LIMIT',
# 'position_side':              'BOTH',
# 'order_realized_profit':      '0',
# 'unicorn_fied':               ['binance.com-futures', '0.11.0']
# }
# @dataclass
# class OrderTradeUpdateUserData:
#     # 'stream_type':'ORDER_TRADE_UPDATE'


# {
# 'stream_type': 'ACCOUNT_UPDATE',
# 'event_type': 'ACCOUNT_UPDATE',
# 'event_time': 1635393515324,
# 'transaction': 1635393515321,
# 'event_reason':
# 'ORDER',
# 'balances': [
#               {
#                   'asset': 'USDT',
#                   'wallet_balance': '9997.42853339',
#                   'cross_wallet_balance': '9997.42853339'
#               }
#             ],
# 'positions': [
#               {
#                   'symbol': 'BTCUSDT',
#                   'position_amount': '0.022',
#                   'entry_price': '58913.42000',
#                   'accumulated_realized': '9772.71248036',
#                   'upnl': '0.10459350',
#                   'margin_type': 'cross',
#                   'isolated_wallet': '0',
#                   'position_side': 'BOTH'
#                }
#              ],
# 'unicorn_fied': ['binance.com-futures', '0.11.0']}

# @dataclass
# class AccountUpdateUserData:
#     # 'stream_type': 'ACCOUNT_UPDATE'

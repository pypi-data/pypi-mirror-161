from dataclasses import dataclass
from enum import Enum, unique
from typing import List


@unique
class Assets(Enum):
    BTC_USDT = 'BTCUSDT'
    ETC_USDT = 'ETCUSDT'
    XRP_USDT = 'XRPUSDT'
    EOS_USDT = 'EOSUSDT'
    ETH_USDT = 'ETHUSDT'


@unique
class KLINE_INTERVALS(Enum):
    MINUTE_1 = '1m'
    MINUTE_3 = '3m'
    MINUTE_5 = '5m'
    MINUTE_15 = '15m'
    MINUTE_30 = '30m'

    HOUR_1 = '1h'
    HOUR_2 = '2h'
    HOUR_4 = '4h'
    HOUR_6 = '6h'
    HOUR_8 = '8h'
    HOUR_12 = '12h'

    DAY_1 = '1d'
    DAY_3 = '3d'

    WEEK_1 = '1w'

    MONTH_1 = '1M'


@dataclass
class Strategy:
    Kline: List[KLINE_INTERVALS]
    Asset: List[Assets]

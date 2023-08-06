from dataclasses import dataclass


@dataclass
class Indicator:
    Id: str
    Name: str
    Script: str
    FirstLevel: str
    SecondLevel: str


@dataclass
class SuperTrend(Indicator):
    Value_1: float
    Value_2: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0):
        super().__init__(Id="STD;Supertrend",
                         Name="SuperTrend",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2


@dataclass
class Volume(Indicator):
    Value_1: float
    Value_2: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0):
        super().__init__(Id="",
                         Name="Volume",
                         Script="Volume@tv-basicstudies-176",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2


@dataclass
class TripleMovingAverages(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0, Value_3: float = 0):
        super().__init__(Id="PUB;y784PkOKflCjfhCiCB4ewuC0slMtB8PQ",
                         Name="TripleMovingAverages",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3


@dataclass
class MovingAverageExponential(Indicator):
    Value_1: float

    def __init__(self, Value_1: float = 0):
        super().__init__(Id="STD;EMA",
                         Name="MovingAverageExponential",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1


@dataclass
class MovingAverage(Indicator):
    Value_1: float

    def __init__(self, Value_1: float = 0):
        super().__init__(Id="STD;SMA",
                         Name="MovingAverage",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1


@dataclass
class ATR_StopLossFinder(Indicator):
    Value_1: float
    Value_2: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0, ):
        super().__init__(Id="PUB;d48234236f7345c09e3d9017f8c31070",
                         Name="ATR_StopLossFinder",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2

@dataclass
class Sell_Buy_Rates(Indicator):
    Value_1: float

    def __init__(self, Value_1: float = 0 ):
        super().__init__(Id="PUB;LzjHUC8QDN1HzufYCSLfxaV4b9yR6TMx",
                         Name="Sell_Buy_Rates",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1

@dataclass
class CM_Williams_Vix_Fix(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float
    Value_4: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0, Value_4: float = 0 ):
        super().__init__(Id="PUB;239",
                         Name="CM_Williams_Vix_Fix",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3
        self.Value_4 = Value_4


@dataclass
class Average_True_Range(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float
    Value_4: float

    def __init__(self, Value_1: float = 0):
        super().__init__(Id="STD;Average_True_Range",
                         Name="Average_True_Range",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1




@dataclass
class Awesome_Oscillator(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float
    Value_4: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0, Value_4: float = 0):
        super().__init__(Id="STD;Awesome_Oscillator",
                         Name="Awesome_Oscillator",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3
        self.Value_4 = Value_4

@dataclass
class ATRPIPS_LB(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float
    Value_4: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0, Value_4: float = 0):
        super().__init__(Id="PUB;1336",
                         Name="ATRPIPS_LB",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3
        self.Value_4 = Value_4
        # Там вроде 5 значений


@dataclass
class Stochastic(Indicator):
    Value_1: float
    Value_2: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0):
        super().__init__(Id="STD;Stochastic",
                         Name="Stochastic",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2

@dataclass
class VStop(Indicator):
    Value_1: float
    Value_2: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0):
        super().__init__(Id="STD;Volatility_Stop",
                         Name="Volatility_Stop",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2


@dataclass
class Bollinger_Bands(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0):
        super().__init__(Id="STD;Bollinger_Bands",
                         Name="Bollinger_Bands",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3


@dataclass
class VMA_LB(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0):
        super().__init__(Id="PUB;812",
                         Name="VMA_LB",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2 # обычно равен  1
        self.Value_3 = Value_3 # обычно равен  1


@dataclass
class StopAR(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0):
        super().__init__(Id="PUB;931",
                         Name="StopAR",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3


@dataclass
class RSI(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float
    Value_4: float
    Value_5: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0,Value_4: float = 0,Value_5: float = 0 ):
        super().__init__(Id="STD;RSI",
                         Name="RSI",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3 # обычно 1е+100
        self.Value_4 = Value_4 # обычно 1е+100
        self.Value_5 = Value_5 # обычно 1е+100


@dataclass
class RSI(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float
    Value_4: float
    Value_5: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0,Value_3: float = 0,Value_4: float = 0,Value_5: float = 0 ):
        super().__init__(Id="PUB;PJRHjaFt92XFjIpzR2orwyvOKNaJRdSB",
                         Name="RSI",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3 # обычно 1е+100
        self.Value_4 = Value_4 # обычно 1е+100
        self.Value_5 = Value_5 # обычно 1е+100




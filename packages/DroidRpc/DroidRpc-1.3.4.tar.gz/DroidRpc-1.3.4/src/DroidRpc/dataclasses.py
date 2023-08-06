# Contains the dataclasses used by the client generator function

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class create_inputs:
    ticker: str
    spot_date: str
    investment_amount: float
    bot_id: str
    margin: int = 1
    price: float = None
    fractionals: bool = False
    tp_multiplier: Optional[float] = None
    sl_multiplier: Optional[float] = None


@dataclass
class hedge_inputs:
    bot_id: str
    ric: str
    current_price: float
    entry_price: float
    last_share_num: float
    last_hedge_delta: float
    investment_amount: float
    bot_cash_balance: float
    stop_loss_price: float
    take_profit_price: float
    expiry: str
    strike: Optional[float] = None
    strike_2: Optional[float] = None
    margin: Optional[int] = 1
    fractionals: Optional[bool] = False
    option_price: Optional[float] = None
    barrier: Optional[float] = None
    current_low_price: Optional[float] = None
    current_high_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_price: Optional[float] = None
    trading_day: Optional[str] = datetime.strftime(datetime.now().date(), "%Y-%m-%d")


@dataclass
class stop_inputs:
    bot_id: str
    ric: str
    current_price: float
    entry_price: float
    last_share_num: float
    last_hedge_delta: float
    investment_amount: float
    bot_cash_balance: float
    stop_loss_price: float
    take_profit_price: float
    expiry: str
    strike: Optional[float] = None
    strike_2: Optional[float] = None
    margin: Optional[int] = 1
    fractionals: Optional[bool] = False
    option_price: Optional[float] = None
    barrier: Optional[float] = None
    current_low_price: Optional[float] = None
    current_high_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_price: Optional[float] = None
    trading_day: Optional[str] = datetime.strftime(datetime.now().date(), "%Y-%m-%d")

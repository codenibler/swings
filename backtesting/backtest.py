import pandas as pd 
import numpy as np
from dataclasses import dataclass
from plot_backtest import plot_backtest
from tqdm import tqdm

# ====== Constants ==========
SPREAD = 0.015
STARTING_EQUITY = 10000
RISK_PER_TRADE = 0.01
DATASET = 'market_data/in_sample1.csv'

# ====== Shift Indicators ==========
df = pd.read_csv('advanced_leg_analytics.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

# ====== Helpers ==========
def _position_size(entry, stop, equity):
    risk_amount = equity * RISK_PER_TRADE
    stop_distance = abs(entry - stop)
    if stop_distance <= 0:  # Adds barriers for impossible trades to happen. 
        return None
    return risk_amount / stop_distance

# ====== Classes ==========
@dataclass
class Trade:
    entry_time: str
    direction: str  # "long" or "short"
    entry_price: float
    stop_loss: float
    take_profit: float
    size: float
    risk_amount: float


@dataclass
class ClosedTrade:
    entry_time: str
    exit_time: str
    direction: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    current_equity: float

@dataclass
class Leg:
    leg_start_price: float
    leg_end_price: float
    leg_start_time: pd.Timestamp
    leg_end_time: pd.Timestamp
    leg_direction: float
    fib50: float
    fib786: float
    leg_pct: float
    entry_price: float
    stop_price: float
    take_profit: float

open_trade = None 
open_leg = False
equity = STARTING_EQUITY
history = []

# ====== Backtester ==========
rows = df.itertuples()
for candle in tqdm(rows, desc='Cranking Backtest.....', total= len(df)):
    
    # ====== Extract Values ==========
    timestamp = getattr(candle, 'datetime')
    open = getattr(candle, 'open')
    high = getattr(candle, 'high')
    low = getattr(candle, 'low')
    close = getattr(candle, 'close')
    leg_direction = getattr(candle, 'leg_direction')
    leg_start_time =pd.to_datetime(getattr(candle, 'leg_start_time'))
    leg_start_price = getattr(candle, 'leg_start_price')
    leg_end_time = pd.to_datetime(getattr(candle, 'leg_end_time'))
    leg_end_price = getattr(candle, 'leg_end_price')
    leg_bars = getattr(candle, 'leg_bars')
    leg_direction = getattr(candle, 'leg_direction')
    fib50 =  getattr(candle, 'fib50') 
    fib786 =  getattr(candle, 'fib786')
    leg_pct =  getattr(candle, 'leg_pct')

    # ====== New Trade Logic ==========
    if open_leg == False:
        if not pd.isna(leg_direction): # If we just closed a leg:
            if leg_pct < 0.0015: # Skip legs smaller than 0.15%
                continue
            open_leg = True
            if leg_direction == 0: # shrot
                direction = 'long' if leg_direction == 1.0 else 'short'
                current_leg = Leg(leg_start_price=leg_start_price, leg_end_price=leg_end_price, leg_direction=direction, 
                                    leg_start_time=leg_start_time, leg_end_time=leg_end_time, fib50=fib50, fib786=fib786, 
                                    leg_pct=leg_pct, entry_price=fib786 - SPREAD, stop_price=leg_start_price, take_profit=leg_end_price)
                size = _position_size(current_leg.entry_price, current_leg.stop_price, equity)
                if not np.isfinite(current_leg.stop_price): 
                    continue
                if size is None:
                    continue
                risk_amount = equity * RISK_PER_TRADE
            else: # long
                direction = 'long' if leg_direction == 1.0 else 'short'
                open_leg = True
                current_leg = Leg(leg_start_price=leg_start_price, leg_end_price=leg_end_price, leg_direction=direction, 
                                    leg_start_time=leg_start_time, leg_end_time=leg_end_time, fib50=fib50, fib786=fib786, 
                                    leg_pct=leg_pct, entry_price=fib786 + SPREAD, stop_price=leg_start_price, take_profit=leg_end_price,)
                size = _position_size(current_leg.entry_price, current_leg.stop_price, equity)
                if not np.isfinite(current_leg.stop_price): 
                    continue
                if size is None:
                    continue
                risk_amount = equity * RISK_PER_TRADE

    # ====== Ongoing Trade Logic ==========
    elif not pd.isna(open_leg) and current_leg.leg_end_time != timestamp:
        trade_closed = False
        if open_trade is None:
            if timestamp - current_leg.leg_end_time > pd.Timedelta(minutes=30):
                open_leg = False
                current_leg = None
                continue
            if direction == 'long':
                if low < current_leg.fib786:
                    open_trade = Trade(timestamp, current_leg.leg_direction, current_leg.entry_price, current_leg.stop_price, current_leg.take_profit, size, risk_amount)
            else:
                if high > current_leg.fib786:
                    open_trade = Trade(timestamp, current_leg.leg_direction, current_leg.entry_price, current_leg.stop_price, current_leg.take_profit, size, risk_amount)
        else:
            if direction == 'long':
                if timestamp - open_trade.entry_time > pd.Timedelta(minutes=30):
                    trade_closed = True
                    exit_price = close - SPREAD
                if high > current_leg.take_profit:
                    trade_closed = True
                    exit_price = current_leg.take_profit - SPREAD
                elif low < current_leg.stop_price:
                    trade_closed = True
                    exit_price = current_leg.stop_price - SPREAD
            else:
                if timestamp - open_trade.entry_time > pd.Timedelta(minutes=30):
                    trade_closed = True
                    exit_price = close + SPREAD
                if low < current_leg.take_profit:
                    trade_closed = True
                    exit_price = current_leg.take_profit + SPREAD
                elif high > current_leg.stop_price:
                    trade_closed = True
                    exit_price = current_leg.stop_price + SPREAD

        if trade_closed:
            if open_trade.direction == 'long':
                pnl = (exit_price - open_trade.entry_price) * open_trade.size
            else:
                pnl = (open_trade.entry_price - exit_price) * open_trade.size
            equity += pnl

            history.append(
                ClosedTrade(
                    entry_time=open_trade.entry_time,
                    exit_time=timestamp,
                    direction=open_trade.direction,
                    entry_price=open_trade.entry_price,
                    exit_price=exit_price,
                    size=open_trade.size,
                    pnl=pnl,
                    current_equity=equity
                )
            )
            open_trade = None
            open_leg = False
            current_leg = None


# ====== Update Trade Logic ==========
wins = sum(1 for t in history if t.pnl > 0)
losses = sum(1 for t in history if t.pnl <= 0)
gross_pnl = sum(t.pnl for t in history)
trades = pd.DataFrame(history)
trades.to_csv("backtest_trades.csv", index=False)
print(f"Trades: {len(history)}  Wins: {wins}  Losses: {losses}")
print(f"Final equity: {equity:.2f}  Net PnL: {equity - STARTING_EQUITY:.2f}")
plot_backtest(df)

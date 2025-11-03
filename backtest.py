import pandas as pd 
import numpy as np
from dataclasses import dataclass
from signals import generate_data
from plot_backtest import plot_backtest
from tqdm import tqdm

# ====== Constants ==========
SPREAD = 0.015
STARTING_EQUITY = 10000
RISK_PER_TRADE = 0.01
ATR_STOP_MULT = 3
DATASET = 'data/CL_1m.csv'

# ====== Shift Indicators ==========
df = generate_data(DATASET).reset_index()
df['datetime'] = pd.to_datetime(df['datetime'])
df[['rsi14', 'atr14']] = df[['rsi14', 'atr14']].shift(1)

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
    exit_reason: str
    current_equity: float

open_trade = None 
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
    atr = getattr(candle, 'atr14')
    swing_low = getattr(candle, 'is_swing_low')
    swing_high = getattr(candle, 'is_swing_high')
    swing_low_price = getattr(candle, 'swing_low')
    swing_high_price = getattr(candle, 'swing_high')
    
    # ====== New Trade Logic ==========
    if open_trade == None:
        if swing_low:
            direction = 'long'
            entry_price = close + SPREAD 
            stop_price = low - atr * ATR_STOP_MULT
            size = _position_size(entry_price, stop_price, equity)
            if not np.isfinite(atr) or not np.isfinite(stop_price): 
                continue
            if size is None:
                continue
            risk_amount = equity * RISK_PER_TRADE
            open_trade = Trade(timestamp, direction, entry_price, stop_price, size, risk_amount)

        if swing_high:
            direction = 'short'
            entry_price = close - SPREAD 
            stop_price = high +  atr * ATR_STOP_MULT
            size = _position_size(entry_price, stop_price, equity)
            if not np.isfinite(atr) or not np.isfinite(stop_price): 
                continue
            if size is None:
                continue
            risk_amount = equity * RISK_PER_TRADE
            open_trade = Trade(timestamp, direction, entry_price, stop_price, size, risk_amount)
    
    # ====== Update Trade Logic ==========
    else: 
        trade_closed = False
        exit_price = close

        exit_reason = "trailing_stop"
        if open_trade.direction == "long":
            if low <= open_trade.stop_loss:
                exit_price = open_trade.stop_loss - SPREAD
                trade_closed = True
        else:
            if high >= open_trade.stop_loss:
                exit_price = open_trade.stop_loss + SPREAD
                trade_closed = True

        if timestamp.weekday() == 4 and timestamp.hour == 16 and timestamp.minute == 59 and not trade_closed:
                exit_price = close - SPREAD if open_trade.direction == 'long' else close + SPREAD 
                exit_reason = "market_close"
                trade_closed = True
        
        if open_trade.direction == "long" and low - atr * ATR_STOP_MULT > open_trade.stop_loss:
            open_trade.stop_loss = float(low - atr * ATR_STOP_MULT)
        elif open_trade.direction == "short" and high + atr * ATR_STOP_MULT < open_trade.stop_loss:
            open_trade.stop_loss = float(high + atr * ATR_STOP_MULT)

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
                    exit_reason=exit_reason,
                    current_equity=equity
                )
            )
            open_trade = None

# ====== Update Trade Logic ==========
wins = sum(1 for t in history if t.pnl > 0)
losses = sum(1 for t in history if t.pnl <= 0)
gross_pnl = sum(t.pnl for t in history)
trades = pd.DataFrame(history)
trades.to_csv("backtest_trades.csv", index=False)
print(f"Trades: {len(history)}  Wins: {wins}  Losses: {losses}")
print(f"Final equity: {equity:.2f}  Net PnL: {equity - STARTING_EQUITY:.2f}")
plot_backtest(df)

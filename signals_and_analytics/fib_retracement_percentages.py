import pandas as pd 
from dataclasses import dataclass

@dataclass
class Leg:
    leg_start_price: float
    leg_end_price: float
    leg_start_time: pd.Timestamp
    leg_end_time: pd.Timestamp
    leg_direction: float
    fib25: float
    fib50: float
    fib75: float

df = pd.read_csv("pivot_data/advanced_leg_analytics_30m.csv")
df['leg_start_time'] = pd.to_datetime(df['leg_start_time'])
df['leg_end_time'] = pd.to_datetime(df['leg_end_time'])
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.set_index('datetime')

count25, count50, count75, count100, total_legs = 0, 0, 0, 0, 0
testing25, testing50, testing75 = False, False, False
current_leg = None

for candle in df.itertuples():
    if candle.leg_direction in [1.0, 0]:
        direction = 'long' if candle.leg_direction == 1.0 else 'short' 
        current_leg = Leg(candle.leg_start_price, candle.leg_end_price, candle.leg_start_time, candle.leg_end_time,
                            direction, candle.fib25, candle.fib50, candle.fib75)
        if current_leg.direction == 'long':
            window = df.loc[candle.leg_end_time:candle.leg_end_time + pd.Timedelta(minutes=30)]


        else:
            


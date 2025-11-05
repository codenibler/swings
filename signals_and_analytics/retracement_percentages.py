import pandas as pd 
from dataclasses import dataclass

@dataclass
class Leg:
    direction: int
    start_price: float
    end_price: float
    duration: int
    start_ts: pd.Timestamp
    end_ts: pd.Timestamp
    fib50: float
    fib75: float
    fib25: float
    hit50: bool
    hit75: bool
    hit100: bool
    hit25: float

df = pd.read_csv('pivot_data/advanced_leg_analytics_30m_NY_LDN.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.set_index('datetime')

df['leg_start_time'] = pd.to_datetime(df['leg_start_time'])
df['leg_end_time'] = pd.to_datetime(df['leg_end_time'])

score25 = 0
score50 = 0
score75 = 0
score100 = 0
leg_count = 0
leg_lengths = 0
current_leg = None

for candle in df.itertuples():
    # Found a leg 
    if current_leg is None:
        if candle.leg_direction in [0,1.0]:
            current_leg = Leg(direction=candle.leg_direction, 
                                start_price=candle.leg_start_price,
                                end_price=candle.leg_end_price,
                                duration=candle.leg_bars,
                                start_ts = candle.leg_start_time,
                                end_ts = candle.leg_end_time,
                                fib25 = candle.fib25,
                                fib50 = candle.fib50,
                                fib75 = candle.fib75,
                                hit25=False,
                                hit50= False,
                                hit75=False,
                                hit100=False)
            leg_count += 1
            leg_lengths += candle.leg_bars
    else:
        # Found new leg before retracement happened. 
        if candle.leg_direction in [0,1.0] and candle.Index != current_leg.start_ts:
            current_leg = Leg(direction=candle.leg_direction, 
                        start_price=candle.leg_start_price,
                        end_price=candle.leg_end_price,
                        duration=candle.leg_bars,
                        start_ts = candle.leg_start_time,
                        end_ts = candle.leg_end_time,
                        fib25 = candle.fib25,
                        fib50 = candle.fib50,
                        fib75 = candle.fib75,
                        hit25 = False,
                        hit50= False,
                        hit75=False,
                        hit100=False)
            leg_count += 1
            leg_lengths += candle.leg_bars
        else:
            if current_leg.direction == 1:
                if candle.low <= current_leg.fib25 and current_leg.hit25 != True:
                    score25 += 1
                    df.loc[current_leg.end_ts, 'fib25_retracement'] = True
                    current_leg.hit25 = True
                if candle.low <= current_leg.fib50 and current_leg.hit50 != True:
                    score50 += 1
                    df.loc[current_leg.end_ts, 'fib50_retracement'] = True
                    current_leg.hit50 = True
                if candle.low <= current_leg.fib75 and current_leg.hit75 != True:
                    score75 += 1
                    df.loc[current_leg.end_ts, 'fib75_retracement'] = True
                    current_leg.hit75 = True
                if candle.low <= current_leg.start_price and current_leg.hit100 != True:
                    score100 += 1
                    df.loc[current_leg.end_ts, 'fib100_retracement'] = True
                    current_leg.hit100 = True
            else:
                if candle.high >= current_leg.fib25 and current_leg.hit25 != True:
                    score25 += 1
                    df.loc[current_leg.end_ts, 'fib25_retracement'] = True
                    current_leg.hit25 = True
                if candle.high >= current_leg.fib50 and current_leg.hit50 != True:
                    score50 += 1
                    df.loc[current_leg.end_ts, 'fib50_retracement'] = True
                    current_leg.hit50 = True
                if candle.high >= current_leg.fib75  and current_leg.hit75 != True:
                    score75 += 1
                    df.loc[current_leg.end_ts, 'fib75_retracement'] = True
                    current_leg.hit75 = True
                if candle.high >= current_leg.start_price and current_leg.hit100 != True:
                    score100 += 1
                    df.loc[current_leg.end_ts, 'fib100_retracement'] = True
                    current_leg.hit100 = True


print(" ===== RESULTS =====")
print(f"Percentage of Retracement to Fib25:  {(score25/leg_count) * 100}")
print(f"Percentage of Retracement to Fib50:  {(score50/leg_count) * 100}")
print(f"Percentage of Retracement to Fib75: {(score75/leg_count) * 100}")
print(f"Percentage of Retracement to Fib100: {(score100/leg_count) * 100}")
print("=================================================")
print(f"Legs Considered: {leg_count}")
print(f"Average Leg Length: {(leg_lengths/leg_count)} Bars")
df.to_csv('pivot_data/advanced_leg_analytics_30m_NY_LDN.csv')



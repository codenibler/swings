import pandas as pd 
from dataclasses import dataclass

@dataclass
class Leg:
    leg_start_price: float
    leg_end_price: float
    leg_start_time: pd.Timestamp
    leg_end_time: pd.Timestamp
    leg_direction: str
    fib25: float
    fib50: float
    fib75: float

df = pd.read_csv("pivot_data/advanced_leg_analytics_30m_NY_LDN.csv")
df['leg_start_time'] = pd.to_datetime(df['leg_start_time'])
df['leg_end_time'] = pd.to_datetime(df['leg_end_time'])
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.set_index('datetime')

count25, count50, count75, count100, no_retrace, total_legs = 0, 0, 0, 0, 0, 0

testing25, testing50, testing75 = False, False, False
current_leg = None

for candle in df.itertuples():
    if candle.leg_direction in [1.0, 0]:
        testing25, testing50, testing75 = False, False, False
        direction = 'long' if candle.leg_direction == 1.0 else 'short' 
        current_leg = Leg(candle.leg_start_price, candle.leg_end_price, candle.leg_start_time, candle.leg_end_time,
                            direction, candle.fib25, candle.fib50, candle.fib75)
        total_legs += 1
        if current_leg.leg_direction == 'long':
            year = current_leg.leg_end_time.year
            month = current_leg.leg_end_time.month
            day = current_leg.leg_end_time.day
            window = df.loc[current_leg.leg_end_time:]
            window = window.iloc[1:] # Remove the cnadle that finished the leg. 
            for candle in window.itertuples(): 
                if candle.low <= current_leg.leg_start_price:
                    count100 += 1
                    current_leg = None
                    break
                elif candle.low <= current_leg.fib75:
                    testing75 = True
                elif candle.low <= current_leg.fib50 and not testing75:
                    testing50 = True
                elif candle.low <= current_leg.fib25 and not (testing75 or testing50):
                    testing25 = True

                if candle.high >= current_leg.leg_end_price:
                    if testing75:
                        count75 += 1
                        current_leg = None
                        break
                    elif testing50:
                        count50 += 1
                        current_leg = None
                        break

                    elif testing25:
                        count25 += 1
                        current_leg = None
                        break

                    else:
                        no_retrace += 1
                        current_leg = None
                        break

        else: # Short
            year = current_leg.leg_end_time.year
            month = current_leg.leg_end_time.month
            day = current_leg.leg_end_time.day
            window = df.loc[current_leg.leg_end_time:]
            window = window.iloc[1:] # Remove the candle that finished the leg. 
            for candle in window.itertuples(): 
                if candle.high >= current_leg.leg_start_price:
                    count100 += 1
                    current_leg = None
                    break
                elif candle.high >= current_leg.fib75:
                    testing75 = True
                elif candle.high >= current_leg.fib50 and not testing75:
                    testing50 = True
                elif candle.high >= current_leg.fib25 and not (testing75 or testing50):
                    testing25 = True

                if candle.low <= current_leg.leg_end_price:
                    if testing75:
                        count75 += 1
                        current_leg = None
                        break
                    elif testing50:
                        count50 += 1
                        current_leg = None
                        break

                    elif testing25:
                        count25 += 1
                        current_leg = None
                        break

                    else:
                        no_retrace += 1
                        current_leg = None
                        break

pct25 = round((count25 / total_legs) * 100, 2)
pct50 = round((count50 / total_legs) * 100, 2)
pct75 = round((count75 / total_legs) * 100, 2)

print("======= ANALYSIS =======")
print(f"Total Legs Checked: {total_legs}")
print(f"# of Legs that Retraced Fully: {count100}, or {round(count100/total_legs, 2)*100} %")
print(f"# of Legs that Retraced to 75% and returned to Leg Start: {count75}, or {pct75} %")
print(f"# of Legs that Retraced to 50% and returned to Leg Start: {count50}, or {pct50} %")
print(f"# of Legs that Retraced to 25% and returned to Leg Start: {count25}, or {pct25} %")
print(f"# of Legs that never returned to Leg Start: {no_retrace}, or {round(no_retrace/total_legs, 2)*100} %")

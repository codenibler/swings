import pandas as pd 
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, default='swings.csv')
parser.add_argument('--output', type=str, default='leg_analytics.csv')
args = parser.parse_args()

df = pd.read_csv(f"pivot_data/{args.input}")
df['datetime'] = pd.to_datetime(df['datetime']) 
df = df.set_index('datetime')

recent_hl = None
recent_hl_index = None
recent_lh = None
recent_lh_index = None

# Creation of Legs
for candle in df.itertuples():
    if candle.swing_type == 'HH':
        if recent_hl is not None and recent_hl_index.day == candle.Index.day:
            df.loc[candle.Index, 'leg_start_time'] = recent_hl_index
            df.loc[candle.Index, 'leg_start_price'] = recent_hl 
            df.loc[candle.Index, 'leg_end_time'] = candle.Index
            df.loc[candle.Index, 'leg_end_price'] = candle.high 
            df.loc[candle.Index, 'leg_bars'] = (pd.to_datetime(candle.Index) - pd.to_datetime(recent_hl_index)) / pd.Timedelta(minutes=30) 
            df.loc[candle.Index, 'leg_direction'] = 1    
            recent_hl = None
            recent_hl_index = None
    if candle.swing_type == 'LL':
        if recent_lh is not None and recent_lh_index.day == candle.Index.day:
            df.loc[candle.Index, 'leg_start_time'] = recent_lh_index
            df.loc[candle.Index, 'leg_start_price'] = recent_lh 
            df.loc[candle.Index, 'leg_end_time'] = candle.Index
            df.loc[candle.Index, 'leg_end_price'] = candle.low 
            df.loc[candle.Index, 'leg_bars'] = (pd.to_datetime(candle.Index) - pd.to_datetime(recent_lh_index)) / pd.Timedelta(minutes=30) 
            df.loc[candle.Index, 'leg_direction'] = 0    
            recent_lh = None
            recent_lh_index = None
    if candle.swing_type == 'LH':
        recent_lh = candle.high
        recent_lh_index = candle.Index
        recent_hl = None
        recent_hl_index = None
    if candle.swing_type == 'HL':
        recent_hl = candle.low
        recent_hl_index = candle.Index
        recent_lh = None
        recent_lh_index = None

# Additional Leg Info
for candle in df.itertuples():
    if candle.leg_direction in [1.0, 0]:
        df.loc[candle.Index, 'leg_magnitude'] = abs(candle.leg_end_price - candle.leg_start_price)
        df.loc[candle.Index, 'leg_pct'] = abs(candle.leg_end_price - candle.leg_start_price) / candle.leg_start_price
        df.loc[candle.Index, 'avg_volume'] = (df[candle.leg_start_time:candle.leg_end_time]['volume'].sum()) / candle.leg_bars        

for candle in df.itertuples():
    if not pd.isna(candle.leg_direction):
        if candle.leg_direction == 1.0:
            df.loc[candle.Index, 'fib25'] = round(candle.leg_start_price + 0.75 * (candle.leg_end_price - candle.leg_start_price), 2)                        
            df.loc[candle.Index, 'fib50'] = round(candle.leg_start_price + 0.5 * (candle.leg_end_price - candle.leg_start_price), 2)            
            df.loc[candle.Index, 'fib75'] = round(candle.leg_end_price - 0.75 * (candle.leg_end_price - candle.leg_start_price), 2)
        else:
            df.loc[candle.Index, 'fib25'] = round(candle.leg_end_price + 0.25 * (candle.leg_start_price - candle.leg_end_price), 2)            
            df.loc[candle.Index, 'fib50'] = round(candle.leg_end_price + 0.5 * (candle.leg_start_price - candle.leg_end_price), 2)            
            df.loc[candle.Index, 'fib75'] = round(candle.leg_end_price + 0.75 * (candle.leg_start_price - candle.leg_end_price), 2)


df.to_csv(f"pivot_data/{args.output}")

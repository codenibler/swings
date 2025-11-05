import pandas as pd 

df = pd.read_csv('pivot_data/pivots_with_fibs_30m_NY_LDN.csv').set_index('datetime')
df.index = pd.to_datetime(df.index)

for candle in df.itertuples():
    if candle.leg_direction in [1.0, 0]:
        df.loc[candle.Index, 'leg_magnitude'] = abs(candle.leg_end_price - candle.leg_start_price)
        df.loc[candle.Index, 'leg_pct'] = abs(candle.leg_end_price - candle.leg_start_price) / candle.leg_start_price
        df.loc[candle.Index, 'avg_volume'] = (df[candle.leg_start_time:candle.leg_end_time]['volume'].sum()) / candle.leg_bars        

print(f"Number of Legs: {len(df[~df['leg_direction'].isna()])}")
df.to_csv('pivot_data/advanced_leg_analytics_30m_NY_LDN.csv')
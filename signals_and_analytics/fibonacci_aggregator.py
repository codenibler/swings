import pandas as pd 

df = pd.read_csv('pivot_data/pivots_with_legs_30m_NY_LDN.csv')

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

df.to_csv('pivot_data/pivots_with_fibs_30m_NY_LDN.csv')
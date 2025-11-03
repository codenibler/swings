import pandas as pd 

df = pd.read_csv('pivots_with_legs.csv')

for candle in df.itertuples():
    if not pd.isna(candle.leg_direction):
        if candle.leg_direction == 1.0:
            df.loc[candle.Index, 'fib50'] = round(candle.leg_start_price + 0.5 * (candle.leg_end_price - candle.leg_start_price), 2)            
            df.loc[candle.Index, 'fib786'] = round(candle.leg_start_price + 0.786 * (candle.leg_end_price - candle.leg_start_price), 2)
        else:
            df.loc[candle.Index, 'fib50'] = round(candle.leg_end_price + 0.5 * (candle.leg_start_price - candle.leg_end_price), 2)            
            df.loc[candle.Index, 'fib786'] = round(candle.leg_end_price + 0.786 * (candle.leg_start_price - candle.leg_end_price), 2)

df.to_csv('pivots_with_fibs.csv')
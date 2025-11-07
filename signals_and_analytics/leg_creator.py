import pandas as pd 

df = pd.read_csv("pivot_data/pivots_30m_NY_LDN.csv")
df['datetime'] = pd.to_datetime(df['datetime']) 
df = df.set_index('datetime')

recent_hl = None
recent_hl_index = None

recent_lh = None
recent_lh_index = None

""" Takes in df with swings, converts them into legs """

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

df.to_csv("pivot_data/pivots_with_legs_30m_NY_LDN.csv")

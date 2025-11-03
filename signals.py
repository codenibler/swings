import pandas as pd 
import pandas_ta as ta

# LVN STRATEGY
# - Find Leg Patterns: 
#   () LL -> HL -> LH -> HH -> Up Leg
#   () HH -> HL -> LH -> LL -> Down Leg


def generate_data(dataset):
    # =============== Indicators ================
    df = pd.read_csv(dataset).set_index('datetime')
    
    # =============== Swing Logic ===============
    df['PrevHigh'] = df['high'].shift(1)
    df['PrevPrevHigh'] = df['high'].shift(2)
    df['PrevLow'] = df['low'].shift(1)
    df['PrevPrevLow'] = df['low'].shift(2)
    swing_lows = (
        (df['PrevLow'] <= df['low']) &
        (df['PrevLow'] <= df['PrevPrevLow'])
    )
    swing_highs= (
        (df['PrevHigh'] >= df['high']) &
        (df['PrevHigh'] >= df['PrevPrevHigh'])
    )
    df['swing_high'] = swing_highs.shift(-1) # CONSIDER SHIFT FOR VISUALIZATION
    df['swing_low'] = swing_lows.shift(-1) # CONSIDER SHIFT FOR VISUALIZATION

    # mark the index (or position) whenever a swing high occurs
    df.loc[df['swing_high'], 'last_swing_high_idx'] = df.index[df['swing_high']]
    df['last_swing_high_idx'] = df['last_swing_high_idx'].ffill()        

    higher_highs = (
        (df[df['swing_high']['high'] >  df.iloc['last_swing_high_idx']['high']])
    )
    lower_lows = (
        (df[df['swing_low']['low'] >  df.iloc['last_swing_low_idx']['low']])
    )
    df['higher_high'] = higher_highs
    df['lower_low'] = lower_lows
    lower_high = (
        df[~df['swing_high']['higher_high']]
    )
    lower_high = (
        df[~df['swing_high']['higher_high']]
    )

    df.drop(columns=['PrevHigh', 'PrevLow', 'PrevPrevLow', 'PrevPrevHigh', 'last_swing_high_idx'])
    
    print(f"Candles: {len(df)}")
    print(f"Higher Highs: {len(df[df['higher_high'] == True])}")
    print(f"Lower Highs: {len(df[df['lower_high'] == True])}")
    print(f"Higher Lows: {len(df[df['higher_low'] == True])}")
    print(f"Lower Lows: {len(df[df['lower_low'] == True])}")

    df = df.dropna()
    
    # =============== Cleaning ===============
    df.to_csv('pivots.csv')
    return df

if __name__ == "__main__":
    generate_data('data/in_sample1.csv')

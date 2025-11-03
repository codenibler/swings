import numpy as np
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

    swing_high_candidates = (
        (df['PrevHigh'] >= df['high']) &
        (df['PrevHigh'] >= df['PrevPrevHigh'])
    )
    swing_low_candidates = (
        (df['PrevLow'] <= df['low']) &
        (df['PrevLow'] <= df['PrevPrevLow'])
    )

    df['swing_high'] = swing_high_candidates.shift(-1, fill_value=False)
    df['swing_low'] = swing_low_candidates.shift(-1, fill_value=False)

    df['swing_high_price'] = df['high'].where(df['swing_high'])
    df['swing_low_price'] = df['low'].where(df['swing_low'])

    prev_swing_high_price = (
        df['swing_high_price'].where(df['swing_high']).ffill().shift()
    )
    prev_swing_low_price = (
        df['swing_low_price'].where(df['swing_low']).ffill().shift()
    )

    df['higher_high'] = False
    df['lower_high'] = False
    df['higher_low'] = False
    df['lower_low'] = False

    high_mask = df['swing_high'] & prev_swing_high_price.notna()
    low_mask = df['swing_low'] & prev_swing_low_price.notna()

    df.loc[high_mask, 'higher_high'] = df.loc[high_mask, 'swing_high_price'] > prev_swing_high_price[high_mask]
    df.loc[high_mask, 'lower_high'] = ~df.loc[high_mask, 'higher_high']

    df.loc[low_mask, 'lower_low'] = df.loc[low_mask, 'swing_low_price'] < prev_swing_low_price[low_mask]
    df.loc[low_mask, 'higher_low'] = ~df.loc[low_mask, 'lower_low']

    df.drop(
        columns=['PrevHigh', 'PrevPrevHigh', 'PrevLow', 'PrevPrevLow'],
        inplace=True
    )

    print(f"Candles: {len(df)}")
    print(f"Swing Highs: {df['swing_high'].sum()}")
    print(f"Swing Lows: {df['swing_low'].sum()}")
    print(f"Higher Highs: {df['higher_high'].sum()}")
    print(f"Lower Highs: {df['lower_high'].sum()}")
    print(f"Higher Lows: {df['higher_low'].sum()}")
    print(f"Lower Lows: {df['lower_low'].sum()}")

    # =============== Cleaning ===============
    df.to_csv('pivots.csv')
    return df


if __name__ == "__main__":
    generate_data('data/in_sample1.csv')

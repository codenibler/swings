import pandas as pd 
import pandas_ta as ta
from ta.trend import ZigZagIndicator

# Set general, underlying market state through longer term EMAs. 
# Hunt micro-reversals with swings and confluence. 

def generate_data(dataset):
    # =============== Indicators ================
    df = pd.read_csv(dataset).set_index('datetime')
    df['atr14'] = ta.atr(high=df['high'], low=df['low'], close=df['close'], length=14, mamode='ema')
    df['rsi14'] = ta.rsi(df['close'], length=14)
    zz = ZigZagIndicator(df['High'], df['Low'], up_thresh=0.05, down_thresh=0.05)
    print(zz)

    # =============== Swing Logic ===============
    df['PrevHigh'] = df['high'].shift(1)
    df['PrevLow'] = df['low'].shift(1)
    df = df.drop(
        columns=[
            'PrevHigh',
            'PrevLow',
        ]
    )
    # =============== Cleaning ===============
    df = df.iloc[50:] # Ignore lines with no EMA. 
    return df

if __name__ == "__main__":
    generate_data('data/in_sample1.csv')

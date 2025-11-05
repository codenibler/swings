import pandas as pd 

df = pd.read_csv("market_data/CL_30m.csv")
df['datetime'] = pd.to_datetime(df['datetime']) - pd.Timedelta(minutes=30)
df.index = df.index 
df = df.set_index('datetime')
df = df.between_time('03:00', '17:00')
df.to_csv("CL_30m_NY.csv")
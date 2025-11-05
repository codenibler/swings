import pandas as pd 
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

df = pd.read_csv('CL_30m_NY.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

fig = go.Figure(
    go.Candlestick(
        x = df['datetime'],
        high=df['high'],
        low=df['low'],
        open=df['open'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )
)

fig.show()
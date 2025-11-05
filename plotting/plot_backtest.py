import pandas as pd 
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

def plot_backtest(data):
    data['datetime'] = pd.to_datetime(data['datetime'])
    trades = pd.read_csv('backtest_trades.csv', parse_dates=['entry_time', 'exit_time'])
    df = data.merge(trades, left_on='datetime', right_on='entry_time', how='outer')
    df['equity_curve'] = df['current_equity'].ffill()
    fig = make_subplots(
        rows=2, 
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0,
        row_heights=[0.7, 0.3],
        row_titles=('Trades', 'Equity')
    ) 

    # ============ PRICE AND INDICATORS ================
    traces = (
        go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='mediumseagreen',
            decreasing_line_color='indianred',
            name='Price'
        ),
    )
    fig.add_traces(traces, rows=1, cols=1)


    # ============ PLOT ENTRIES ================
    fig.add_trace(
        go.Scatter(
            x=df["entry_time"][df['direction'] == 'long'],
            y=df.loc[df['direction'] == 'long', 'entry_price'],
            mode="markers",
            marker=dict(symbol="triangle-up", size=12, color="#2ecc71", line=dict(width=1,color="white")),
            name="LONG ENTRY",
            customdata=df.loc[df['direction'] == 'long', ['size']].to_numpy(),
            hovertemplate="Long Entry<br>Time: %{x|%Y-%m-%d %H:%M}<br>Fill Price: %{y:.5f}<br>Position Size: %{customdata[0]:,.0f}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df["exit_time"][df['direction'] == 'long'],
            y=df.loc[df['direction'] == 'long', 'exit_price'],
            mode="markers",
            marker=dict(symbol="triangle-down", size=12, color="#e74c3c", line=dict(width=1,color="white")),
            name="LONG EXIT",
            customdata=df.loc[df['direction'] == 'long', ['size', 'pnl']].to_numpy(),
            hovertemplate="Long Exit<br>Time: %{x|%Y-%m-%d %H:%M}<br>Fill Price: %{y:.5f}<br>Position Size: %{customdata[0]:,.0f}<br>PnL: %{customdata[1]:+.2f}<br>Exit: %{customdata[2]}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df["entry_time"][df['direction'] == 'short'],
            y=df.loc[df['direction'] == 'short', 'entry_price'],
            mode="markers",
            marker=dict(symbol="triangle-down", size=12, color="#3498db", line=dict(width=1,color="white")),
            name="SHORT ENTRY",
            customdata=df.loc[df['direction'] == 'short', ['size']].to_numpy(),
            hovertemplate="Short Entry<br>Time: %{x|%Y-%m-%d %H:%M}<br>Fill Price: %{y:.5f}<br>Position Size: %{customdata[0]:,.0f}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df["exit_time"][df['direction'] == 'short'],
            y=df.loc[df['direction'] == 'short', 'exit_price'],
            mode="markers",
            marker=dict(symbol="triangle-up", size=12, color="#9b59b6", line=dict(width=1,color="white")),
            name="SHORT EXIT",
            customdata=df.loc[df['direction'] == 'short', ['size', 'pnl']].to_numpy(),
            hovertemplate="Short Exit<br>Time: %{x|%Y-%m-%d %H:%M}<br>Fill Price: %{y:.5f}<br>Position Size: %{customdata[0]:,.0f}<br>PnL: %{customdata[1]:+.2f}<br>Exit: %{customdata[2]}<extra></extra>"
        ),
        row=1,
        col=1
    )   
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time']) & (data['leg_pct'] > 0.0015)],
            y=data['fib50'][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time']) & (data['leg_pct'] > 0.0015)],
            mode="markers",
            marker=dict(color='green'),
            name="FIB 50",
        ),
        row=1,
        col=1
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time']) & (data['leg_pct'] > 0.0015)],
            y=data['fib786'][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time']) & (data['leg_pct'] > 0.0015)],
            mode="markers",
            marker=dict(color='brown'),
            name="FIB 786",
        ),
        row=1,
        col=1
    ),
    legs = data.dropna(subset=["leg_start_time", "leg_end_time", "leg_start_price", "leg_end_price"])
    legs = legs[legs['leg_pct'] > 0.0015]

    def _leg_color(row):
        return "#2ca02c" if row.leg_end_price >= row.leg_start_price else "#d62728"

    for row in legs.itertuples():
        color = _leg_color(row)
        fig.add_trace(
            go.Scatter(
                x=[row.leg_start_time, row.leg_end_time],
                y=[row.leg_start_price, row.leg_end_price],
                mode="lines+markers+text",
                line=dict(color=color, width=2),
                marker=dict(size=8, color=color),
                text=[f"{'LH' if row.swing_type == 'LL' else 'HL'}", f"{row.swing_type}"],
                textposition="top center",
                name="Leg",
                showlegend=False,
            )
        )
    
    # ============ EQUITY ================
    traces = (
        go.Scatter(
                x=df['datetime'],
                y=df['equity_curve'],
                mode='lines',
                line=dict(color="purple", width=3),
                name="Equity"
        )
    )
    fig.add_traces(traces, rows=2, cols=1)


    # ============ PLOT ================
    fig.update_layout(
        title='Minute CL Chart',
        xaxis_title='Time',
        yaxis_title='Price'
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()

if __name__ == "__main__":
    plot_backtest(pd.read_csv('data/in_sample1.csv'))
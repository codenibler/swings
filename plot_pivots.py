import pandas as pd
import plotly.graph_objects as go


def main():
    data = pd.read_csv("pivots_with_legs.csv", parse_dates=["datetime"]).tail(10000)

    pivot_high = data["high"].where(data["swing_high"])
    pivot_low = data["low"].where(data["swing_low"])

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=data["datetime"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            increasing_line_color="mediumseagreen",
            decreasing_line_color="indianred",
            name="Price",
        )
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][data['swing_type'] == 'HH'],
            y=data.loc[data['swing_type'] == 'HH', 'high'],
            mode="markers+text",
            marker=dict(symbol="triangle-down", size=12, color="firebrick", line=dict(width=1,color="white")),
            text=["HH"] * (data['swing_type'] == 'HH').sum(),
            textposition="top center",
            name="HH",
        )
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][data['swing_type'] == 'HL'],
            y=data.loc[data['swing_type'] == 'HL', 'low'],
            mode="markers+text",
            marker=dict(symbol="triangle-up", size=12, color="seagreen", line=dict(width=1,color="white")),
            text=["HL"] * (data['swing_type'] == 'HL').sum(),
            textposition="bottom center",
            name="HL",
        )
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][data['swing_type'] == 'LL'],
            y=data.loc[data['swing_type'] == 'LL', 'low'],
            mode="markers+text",
            marker=dict(symbol="triangle-up", size=12, color="green", line=dict(width=1,color="white")),
            text=["LL"] * (data['swing_type'] == 'LL').sum(),
            textposition="bottom center",
            name="LL",
        )
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][data['swing_type'] == 'LH'],
            y=data.loc[data['swing_type'] == 'LH', 'high'],
            mode="markers+text",
            marker=dict(symbol="triangle-down", size=12, color="firebrick", line=dict(width=1,color="white")),
            text=["LH"] * (data['swing_type'] == 'LH').sum(),
            textposition="bottom center",
            name="LH",
        )
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][(data['datetime'] > data['leg_start_time']) & (data['datetime'] < data['leg_end_time']) & (data['leg_direction'] == 1)],
            y=data['high'],
            mode="lines",
            line=dict(color='Purple', width=3),
            name="Up Leg",
        )
    ),

    fig.update_layout(
        title="Pivot Points",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
    )

    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[16, 9], pattern="hour"),
        ]
    )

    fig.show()


if __name__ == "__main__":
    main()

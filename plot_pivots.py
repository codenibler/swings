import pandas as pd
import plotly.graph_objects as go


def main():
    data = pd.read_csv("cleaned_cl.csv", parse_dates=["datetime"]).tail(10000)

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
    )
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][data['swing_high']],
            y=data.loc[data['swing_high'], 'high'],
            mode="lines",
            line=dict(color="#1f77b4", width=3),
            connectgaps=False,
            name="Pivot High",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data["datetime"][data['swing_low']],
            y=data.loc[data['swing_low'], 'low'],
            mode="lines",
            line=dict(color="#d62728", width=3),
            connectgaps=False,
            name="Pivot Low",
        )
    )

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

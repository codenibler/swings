import pandas as pd
import plotly.graph_objects as go


def main():
    data = pd.read_csv("pivots.csv", parse_dates=["datetime"]).tail(10000)

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
            x=data.loc[data['swing_high'], 'datetime'],
            y=data.loc[data['swing_high'], 'swing_high_price'],
            mode="markers+text",
            marker=dict(color="#1f77b4", size=8),
            text=data.loc[data['swing_high'], 'higher_high'].map(
                {True: "HH", False: "LH"}
            ),
            textposition="top center",
            name="Swing Highs",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.loc[data['swing_low'], 'datetime'],
            y=data.loc[data['swing_low'], 'swing_low_price'],
            mode="markers+text",
            marker=dict(color="#d62728", size=8),
            text=data.loc[data['swing_low'], 'lower_low'].map(
                {True: "LL", False: "HL"}
            ),
            textposition="bottom center",
            name="Swing Lows",
        )
    )

    fig.update_layout(
        title="Codex Pivot Structure (HH, LH, HL, LL)",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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

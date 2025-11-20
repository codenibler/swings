import pandas as pd
import plotly.graph_objects as go


def _parse_datetime_columns(df: pd.DataFrame, columns):
    """Safely parse datetime columns that may contain NaNs."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def _plot_legs(fig: go.Figure, data: pd.DataFrame) -> None:
    """Overlay price legs, with colour by direction."""
    legs = data.dropna(subset=["leg_start_time", "leg_end_time", "leg_start_price", "leg_end_price"])
    if legs.empty:
        return

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


def main():
    data = pd.read_csv("pivot_data/advanced_leg_analytics_30m_NY_LDN.csv")
    data = _parse_datetime_columns(data, ["datetime", "leg_start_time", "leg_end_time"])

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
            x=data["datetime"][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time'])],
            y=data['fib75'][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time'])],
            mode="markers",
            marker=dict(color='#f41d0b', symbol='diamond-wide', size=25),
            name="FIB 75",
        )
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time'])],
            y=data['fib50'][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time'])],
            mode="markers",
            marker=dict(color='#e58b1a', symbol='diamond-wide',size=25),
            name="FIB 50",
        )
    ),
    fig.add_trace(
        go.Scatter(
            x=data["datetime"][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time'])],
            y=data['fib25'][(data['datetime'] >= data['leg_start_time']) & (data['datetime'] <= data['leg_end_time'])],
            mode="markers",
            marker=dict(color='#9fac15', symbol='diamond-wide',size=25),
            name="FIB 25",
        )
    ),



    # _plot_swings(fig, data)
    _plot_legs(fig, data)

    fig.update_layout(
        title="Pivot Points with Legs",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    fig.show()


if __name__ == "__main__":
    main()

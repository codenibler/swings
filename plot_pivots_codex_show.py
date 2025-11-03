import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


def _parse_datetime_columns(df: pd.DataFrame, columns) -> pd.DataFrame:
    """Convert target columns to datetime, tolerating NaNs."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def _plot_swings(fig: go.Figure, data: pd.DataFrame) -> None:
    """Annotate HH / HL / LH / LL swings directly on the price series."""
    swing_markers = [
        ("HH", "high", dict(symbol="triangle-down", size=12, color="firebrick", line=dict(width=1, color="white")), "bottom center"),
        ("LH", "high", dict(symbol="triangle-down", size=12, color="#e377c2", line=dict(width=1, color="white")), "bottom center"),
        ("LL", "low", dict(symbol="triangle-up", size=12, color="green", line=dict(width=1, color="white")), "top center"),
        ("HL", "low", dict(symbol="triangle-up", size=12, color="seagreen", line=dict(width=1, color="white")), "top center"),
    ]

    for label, price_col, marker, text_position in swing_markers:
        mask = data["swing_type"] == label
        if mask.any():
            fig.add_trace(
                go.Scatter(
                    x=data.loc[mask, "datetime"],
                    y=data.loc[mask, price_col],
                    mode="markers+text",
                    marker=marker,
                    text=[label] * int(mask.sum()),
                    textposition=text_position,
                    name=label,
                )
            )


def _plot_legs(fig: go.Figure, data: pd.DataFrame) -> None:
    """Overlay leg segments using their recorded start/end metadata."""
    legs = data.dropna(subset=["leg_start_time", "leg_end_time", "leg_start_price", "leg_end_price"])
    if legs.empty:
        return

    for row in legs.itertuples():
        color = "#2ca02c" if row.leg_end_price >= row.leg_start_price else "#d62728"
        fig.add_trace(
            go.Scatter(
                x=[row.leg_start_time, row.leg_end_time],
                y=[row.leg_start_price, row.leg_end_price],
                mode="lines+markers+text",
                line=dict(color=color, width=2),
                marker=dict(size=8, color=color),
                text=[row.swing_type, row.swing_type],
                textposition="top center",
                name="Leg",
                showlegend=False,
            )
        )


def _plot_fibonacci(fig: go.Figure, data: pd.DataFrame) -> None:
    """Add 50% and 78.6% retracement lines for each leg when available."""
    fib_cols = ["fib50", "fib786"]
    available = [col for col in fib_cols if col in data.columns]
    if not available:
        return

    fib_legs = data.dropna(subset=["leg_start_time", "leg_end_time"])
    if fib_legs.empty:
        return

    legend_added = {col: False for col in available}

    for row in fib_legs.itertuples():
        x_range = [row.leg_start_time, row.leg_end_time]
        if "fib50" in available and pd.notna(row.fib50):
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=[row.fib50, row.fib50],
                    mode="lines+text",
                    line=dict(color="#9467bd", dash="dash"),
                    text=["50%", ""],
                    textposition="top right",
                    name="Fib 50%",
                    showlegend=not legend_added["fib50"],
                )
            )
            legend_added["fib50"] = True
        if "fib786" in available and pd.notna(row.fib786):
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=[row.fib786, row.fib786],
                    mode="lines+text",
                    line=dict(color="#8c564b", dash="dot"),
                    text=["78.6%", ""],
                    textposition="top right",
                    name="Fib 78.6%",
                    showlegend=not legend_added["fib786"],
                )
            )
            legend_added["fib786"] = True


def main():
    data = pd.read_csv("pivots_with_fibs.csv")
    data = _parse_datetime_columns(
        data,
        ["datetime", "leg_start_time", "leg_end_time"],
    )

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

    _plot_swings(fig, data)
    _plot_legs(fig, data)
    _plot_fibonacci(fig, data)

    fig.update_layout(
        title="Pivot Points with Legs and Fibonacci Levels",
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

    # Force a renderer that does not require opening a local web server when possible.
    if "svg" in pio.renderers:
        pio.renderers.default = "svg"
    fig.show()


if __name__ == "__main__":
    main()

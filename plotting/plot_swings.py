import argparse
import pandas as pd
import plotly.graph_objects as go


def _bool_from_text(series: pd.Series) -> pd.Series:
    """Convert stringified boolean columns to actual booleans."""
    return series.astype(str).str.lower().eq("true")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot swing highs/lows on a price chart.")
    parser.add_argument("--input", default="swings.csv", help="CSV from indicators/swings.py located in pivot_data/")
    args = parser.parse_args()

    df = pd.read_csv(f"pivot_data/{args.input}")
    df["datetime"] = pd.to_datetime(df["datetime"])
    for column in ("swing_high", "swing_low"):
        df[column] = _bool_from_text(df[column])

    fig = go.Figure(
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color="mediumseagreen",
            decreasing_line_color="indianred",
            name="Price",
        )
    )

    swings = (
        ("swing_high", "high", "triangle-up", "Swing Highs", "top center", "#d62728"),
        ("swing_low", "low", "triangle-down", "Swing Lows", "bottom center", "#2ca02c"),
    )
    for column, price_field, symbol, name, text_position, color in swings:
        mask = df[column]
        if mask.any():
            fig.add_trace(
                go.Scatter(
                    x=df.loc[mask, "datetime"],
                    y=df.loc[mask, price_field],
                    text=df.loc[mask, "swing_type"].fillna(""),
                    textposition=text_position,
                    mode="markers+text",
                    marker=dict(color=color, size=10, symbol=symbol),
                    name=name,
                    showlegend=True,
                )
            )

    fig.update_layout(
        title="Price Action with Swing Points",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
    )
    fig.show()


if __name__ == "__main__":
    main()

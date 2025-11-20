import pandas as pd
import plotly.graph_objects as go
import argparse

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="leg_analytics.csv")
    args = parser.parse_args()

    data = pd.read_csv(f"pivot_data/{args.input}")
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

import pandas as pd 

legs = pd.read_csv('advanced_leg_analytics.csv')
legs = legs[~legs['leg_direction'].isna()]
print(legs['leg_pct'].mean())

# Average leg move is .138pct, or 0.001375
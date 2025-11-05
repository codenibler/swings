import pandas as pd 
import numpy as np

df = pd.read_csv('CL_30m_NY.csv')
parts = np.array_split(df, 2)

for index, piece in enumerate(parts, start=1):
    if index in [1]:
        piece.to_csv(f"market_data/in_sample{index}_30m_NY_LDN.csv", index=False)
    else:
        piece.to_csv(f"market_data/out_of_sample{index}_30m_NY_LDN.csv", index=False)

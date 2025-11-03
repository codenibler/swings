import pandas as pd 
import numpy as np

df = pd.read_csv('data/CL_1m.csv')
parts = np.array_split(df, 8)

for index, piece in enumerate(parts, start=1):
    if index in [1,2, 3, 4]:
        piece.to_csv(f"in_sample{index}.csv", index=False)
    else:
        piece.to_csv(f"out_of_sample{index}.csv", index=False)

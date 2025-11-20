import pandas as pd, numpy as np
from scipy import stats as st
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("pivot_data/advanced_leg_analytics_30m_NY_LDN.csv")

# Completed legs + label
legs = df.dropna(subset=["leg_magnitude","leg_pct"]).copy()
legs["retr_full"] = legs["fib100_retracement"].fillna(False).astype(bool).astype(int)

# Features
features = [c for c in ["leg_magnitude","leg_pct","leg_bars","atr","rsi","avg_volume","uptrend"] if c in legs.columns]
if "uptrend" in features: legs["uptrend"] = legs["uptrend"].astype(int)

A = legs[legs.retr_full==1]; B = legs[legs.retr_full==0]
print({"retraced":len(A), "not_retraced":len(B)})

# Welch t-tests
for col in features:
    x = pd.to_numeric(A[col], errors="coerce").dropna()
    y = pd.to_numeric(B[col], errors="coerce").dropna()
    if len(x)>5 and len(y)>5:
        t,p = st.ttest_ind(x,y,equal_var=False)
        print(f"{col:12s} t={t:7.3f} p={p:.3g}")


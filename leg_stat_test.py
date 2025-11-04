import pandas as pd, numpy as np
from scipy import stats as st
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("advanced_leg_analytics.csv")

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

# Logistic with time splits; skip folds that collapse to 1 class
X = legs[features].apply(pd.to_numeric, errors="coerce").fillna(0).values
y = legs["retr_full"].values
tscv = TimeSeriesSplit(n_splits=5)
coefs = []
for tr, te in tscv.split(X):
    if len(set(y[tr])) < 2 or len(set(y[te])) < 2:  # guard against single-class folds
        continue
    m = LogisticRegression(max_iter=1000)
    m.fit(X[tr], y[tr])
    coefs.append(m.coef_[0])

if coefs:
    coef_mean = sum(coefs)/len(coefs)
    for name, c in zip(features, coef_mean):
        print(f"{name:12s}: {c:+.4f}")
else:
    print("All folds collapsed to one class; widen time window or recompute labels.")

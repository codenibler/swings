# An experiment on market structure and patterns

This project tests leg market patterns—marked by sequences like LH -> HH or HL -> LL—and the retracement probabilities of each leg. Findings are at the end of the README. The code grew out of curiosity and could be cleaner or more vectorized, but it serves the purpose. *I hope it serves you for something!*

---

Pipeline to use this repo with your own dataset:

1) Prepare data  
   - Aggregate your dataset into `market_data/`. The repo includes 1 year of Crude Oil CFD data, split into four in-sample sections (first 6 months) and four out-of-sample sections (last 6 months).

2) Generate swings  
   - **indicators/signals.py**  
     Purpose: Generates HH, LL, HL, and LH swings. 
     Usage: `python3 indicators/swings.py --input in_sample/1 --output swings.csv`  
     Outputs: `pivot_data/swings.csv`

3) Plot swings  
   - **plotting/plot_swings.py**  
     Purpose: Allows you to visualize swings generated previously. 
     Usage: `python3 plotting/plot_swings.py --input swings.csv`  
     Outputs: HTML plot in browser

4) Generate legs  
   - **indicators/leg_creator.py**  
     Purpose: Generates swings with HL -> LL or LH -> HH patterns. 
     Usage: `python3 indicators/leg_creator.py --input swings.csv --output leg_analytics`  
     Outputs: `pivot_data/leg_analytics.csv`

5) Plot legs  
   - **plotting/plot_legs.py**  
     Purpose: Allows you to visualize previously generated legs. 
     Usage: `python3 plotting/plot_legs.py --input leg_analytics.csv`  
     Outputs: HTML chart in browser

6) Analyze retracement hit rates  
   - **indicators/hit_pcts.py**  
     Purpose: Shows what percentage of legs retraced to 25%, 50%, 75%, or 100% from the leg end to the dataset end (window adjustable on lines 37 and 75).
     Usage: `python3 indicators/hit_pcts.py --input leg_analytics.csv`  
   
7) Analyze retracement and return rates  
   - **indicators/hit_and_retrace_pcts.py**  
     Purpose: Shows percentage of legs that retraced to 25%, 50%, 75%, or 100%, and then proceeded to come back to the original start of the leg. Return full retracements.csv, then useful for running a correlation between several indicators and legs that collapsed fully. 
     Usage: `python3 indicators/hit_pcts.py --input leg_analytics.csv`  
     Outputs: `pivot_data/full_retracements.csv`
   
8) Run t-tests on leg features  
   - **indicators/leg_t_tests.py**  
     Purpose: Compares feature distributions (e.g., leg magnitude, pct move, bars, ATR, RSI, avg_volume, trend) between legs that fully retraced and those that did not.  
     Usage: `python3 indicators/leg_t_tests.py`

9) Measure penetration depth  
   - **indicators/penetration_depth.py**  
     Purpose: Uses `full_retracements.csv` and `leg_analytics.csv` to report how deep post-leg stop-loss penetrations went (10/20/30/40 pips vs full violations).  
     Usage: `python3 indicators/penetration_depth.py`

WANRING: If you want to use any of these indicators, only backtest considering values after the 3rd candle of the swing. Only at this point is the swing known.  

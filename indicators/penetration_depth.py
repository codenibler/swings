""" FIND WHETHER STOP LOSS PENETRATIONS HAPPEN FULL DEPTH OR LIMITED NUMBER OF PIPS """ 
import pandas as pd 

full = pd.read_csv('pivot_data/full_retracements.csv')
full['end_ts'] = pd.to_datetime(full['end_ts'])
data = pd.read_csv('pivot_data/advanced_leg_analytics_30m_NY_LDN.csv')
data['datetime'] = pd.to_datetime(data['datetime'])

count10, count20, count30, count40, fully = 0,0,0,0,0
deepest = None

for leg in full.itertuples():
    deepest = None
    if leg.direction == 1.0: #long 
        window = data.loc[data['datetime'] > leg.end_ts]
        for candle in window.itertuples():
            penetration_depth = leg.start_price - candle.low
            if penetration_depth > 0.40: # 40 pip max
                fully += 1
                break
            elif penetration_depth > 0.30 and penetration_depth <= 0.40:
                deepest = 40
            elif penetration_depth > 0.20 and penetration_depth <= 0.30 and deepest != 40:
                deepest = 30
            elif penetration_depth > 0.10 and penetration_depth <= 0.20 and deepest not in [40, 30]:
                deepest = 20
            elif penetration_depth > 0.0 and penetration_depth <= 0.10 and deepest not in [40, 30, 20]:
                deepest = 10
            
            if candle.high > leg.end_price:
                if deepest == 40:
                    count40 += 1
                elif deepest == 30:
                    count30 += 1
                elif deepest == 20:
                    count20 += 1
                elif deepest == 10:
                    count10 += 1
                break

    else: #short 
        window = data.loc[data['datetime'] > leg.end_ts]
        for candle in window.itertuples():
            penetration_depth = candle.high - leg.start_price
            if penetration_depth > 0.40: # 40 pip max
                fully += 1
                deepest = None
                break
            elif penetration_depth > 0.30 and penetration_depth <= 0.40:
                deepest = 40
            elif penetration_depth > 0.20 and penetration_depth <= 0.30 and deepest != 40:
                deepest = 30
            elif penetration_depth > 0.10 and penetration_depth <= 0.20 and deepest not in [40, 30]:
                deepest = 20
            elif penetration_depth > 0.0 and penetration_depth <= 0.10 and deepest not in [40, 30, 20]:
                deepest = 10
            
            if candle.low < leg.end_price:
                if deepest == 40:
                    count40 += 1
                elif deepest == 30:
                    count30 += 1
                elif deepest == 20:
                    count20 += 1
                elif deepest == 10:
                    count10 += 1
                break

total = count10 + count20 + count30 + count40 + fully

print(" ===== RESULTS =====")
print(f"Percentage of penetrations only to 10 Pips:  {(count10/total) * 100}")
print(f"Percentage of penetrations only to 20 Pips:  {(count20/total) * 100}")
print(f"Percentage of penetrations only to 30 Pips: {(count30/total) * 100}")
print(f"Percentage of penetrations only to 40 Pips {(count40/total) * 100}")
print(f"Percentage ofFull Violations {(fully/total) * 100}")
print("=================================================")
print(f"Legs Considered: {total}")

                


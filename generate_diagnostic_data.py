import pandas as pd
import numpy as np

np.random.seed(104) 
num_records = 51000

facilities = ['General Hospital A', 'Mercy Medical B', 'Valley Health C', 'Summit Care D']
departments = ['Emergency', 'Surgery', 'ICU', 'Maternity', 'Orthopedics']

data = {
    'record_id': np.arange(100000, 100000 + num_records),
    'date': pd.date_range(start='2025-01-01', periods=num_records, freq='43min'),
    'facility': np.random.choice(facilities, num_records),
    'department': np.random.choice(departments, num_records)
}
df = pd.DataFrame(data)


df['er_wait_time_mins'] = np.random.normal(40, 10, num_records)
weights_er = np.where((df['facility'] == 'Mercy Medical B') | (df['department'] == 'Emergency'), 0.8, 0.05)
anomaly_idx_er = df.sample(frac=0.12, weights=weights_er, random_state=1).index
df.loc[anomaly_idx_er, 'er_wait_time_mins'] = np.random.normal(95, 15, len(anomaly_idx_er))

df['bed_turnover_hrs'] = np.random.normal(1.8, 0.4, num_records)
weights_bed = np.where((df['facility'] == 'General Hospital A') | (df['department'] == 'Maternity'), 0.8, 0.05)
anomaly_idx_bed = df.sample(frac=0.08, weights=weights_bed, random_state=2).index
df.loc[anomaly_idx_bed, 'bed_turnover_hrs'] = np.random.normal(3.5, 0.5, len(anomaly_idx_bed))

df['procurement_cost_usd'] = np.random.normal(390, 15, num_records)
weights_proc = np.where((df['facility'] == 'Summit Care D') | (df['department'] == 'Surgery'), 0.8, 0.05)
anomaly_idx_proc = df.sample(frac=0.10, weights=weights_proc, random_state=3).index
df.loc[anomaly_idx_proc, 'procurement_cost_usd'] = np.random.normal(480, 20, len(anomaly_idx_proc))

df['er_wait_time_mins'] = df['er_wait_time_mins'].clip(lower=0)
df['bed_turnover_hrs'] = df['bed_turnover_hrs'].clip(lower=0)

def calculate_leakage(row):
    er_penalty = max(0, row['er_wait_time_mins'] - 45
    bed_penalty = max(0, row['bed_turnover_hrs'] - 2.0) * 150
    proc_penalty = max(0, row['procurement_cost_usd'] - 400)
    
    return pd.Series([er_penalty, bed_penalty, proc_penalty])

df[['er_leakage', 'bed_leakage', 'proc_leakage']] = df.apply(calculate_leakage, axis=1)

total_leakage = df['er_leakage'].sum() + df['bed_leakage'].sum() + df['proc_leakage'].sum()

print(f"Total Generated Records: {len(df)}")
print(f"Calculated Value at Stake (Efficiency Gap): ${total_leakage:,.2f}")

df_export = df.drop(columns=['er_leakage', 'bed_leakage', 'proc_leakage'])

df_export.to_csv('hospital_operations_data.csv', index=False)
print("Data exported to 'hospital_operations_data.csv'.")

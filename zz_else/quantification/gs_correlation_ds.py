import pandas as pd

path = "/Users/aljoscha/Downloads/zapbench_data_thalamus/ds_thalamic_neurons.csv"
df = pd.read_csv(path)

cols = ["contralateral", "AF56", "tectal_neuropil"]

from scipy.stats import pointbiserialr

for col in cols:
    x = df[col].astype(int)
    y = df["DS magnitude"]

    r, p = pointbiserialr(x, y)
    print(f"{col}: r={r:.3f}, p={p:.3g}")
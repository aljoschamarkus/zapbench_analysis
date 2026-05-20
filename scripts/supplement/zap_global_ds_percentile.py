import h5py as h5
from config import *
import numpy as np

ds_data = h5.File(PATHS.in_data("zap_direction_selectivity.h5"), "r")
ds_vectors = ds_data["magnitude"][:]
print(ds_vectors.shape)
print(np.min(ds_vectors), np.max(ds_vectors))

percentiles = np.arange(0, 105, 5)
info = []

for pct in percentiles:
    threshold_value = np.nanpercentile(ds_vectors, pct)
    kept = (ds_vectors >= threshold_value).sum()
    info.append([pct, threshold_value, kept])

print(info)
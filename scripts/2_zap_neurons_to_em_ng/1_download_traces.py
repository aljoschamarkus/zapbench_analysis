import tensorstore as ts
import h5py as h5
from config import *

f_stim = h5.File(PATHS.in_data("zap_stimulus_turning.h5"), "r")
condition_t = f_stim["condition_t"][:]

ds = ts.open({
    'open': True,
    'driver': GS["zap_traces"][0],
    'kvstore': GS["zap_traces"][1],
}).result()

data = ds[condition_t[0]:condition_t[-1]+1,:].read().result()

with h5.File(PATHS.in_data("zap_traces.h5"), "w") as f:
    dset = f.create_dataset("data", data=data, compression="gzip")
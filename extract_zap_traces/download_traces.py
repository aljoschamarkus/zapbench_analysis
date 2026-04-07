import tensorstore as ts
import h5py as h5
from config import *

f_stim = h5.File(STIM_FILE, "r")
condition_t = f_stim["condition_t"][:]

ds = ts.open({
    'open': True,
    'driver': 'zarr3',
    'kvstore': 'gs://zapbench-release/volumes/20240930/traces'
}).result()

data = ds[condition_t[0]:condition_t[-1]+1,:].read().result()
print(data.shape)

with h5.File(TRACES_FILE, "w") as f:
    dset = f.create_dataset("data", data=data, compression="gzip")
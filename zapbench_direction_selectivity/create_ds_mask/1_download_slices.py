import numpy as np
import tensorstore as ts
from tqdm import tqdm
import h5py as h5
from config import *

os.makedirs(DATA_DIR, exist_ok=True)

f_stim = h5.File(STIM_FILE, "r")
condition_t = f_stim["condition_t"][:]

ds = ts.open({
    'open': True,
    'driver': 'zarr3',
    'kvstore': 'gs://zapbench-release/volumes/20240930/aligned'
}).result()

for i in tqdm(np.arange(VOLUME_LIMS["z_min"], VOLUME_LIMS["z_max"], 1)):
    if os.path.isfile(os.path.join(DATA_DIR, f"zap_data_{i}.h5")):
        continue
    print(f"downloading slice {i}.")
    block = ds[VOLUME_LIMS["x_min"]:VOLUME_LIMS["x_max"],VOLUME_LIMS["y_min"]:VOLUME_LIMS["y_max"],i,condition_t[0]:condition_t[-1]+1].read().result()
    print(f"saving slice {i}.")
    with h5.File(os.path.join(DATA_DIR, f"zap_data_{i}.h5"), "w") as f:
        dset = f.create_dataset("data", data=block, compression="gzip")

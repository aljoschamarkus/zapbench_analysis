import tensorstore as ts
import h5py as h5
from utils import utils
import os
from tqdm import tqdm
import numpy as np

ds = ts.open({
    'open': True,
    'driver': 'zarr3',
    'kvstore': 'gs://zapbench-release/volumes/20240930/aligned'
}).result()

condition_name = 'turning'
inclusive_min, exclusive_max = utils.get_condition_bounds(condition_name)

out_dir = "/Users/aljoscha/Downloads/zapbench_aligned"

x_lim = [700, 951]
y_lim = [450, 851]
z_lim = [15, 36]

for i in tqdm(np.arange(z_lim[0], z_lim[1], 1)):
    if os.path.isfile(os.path.join(out_dir, f"zap_data_{i}.h5")):
        continue
    print(f"downloading slice {i}.")
    block = ds[x_lim[0]:x_lim[1],y_lim[0]:y_lim[1],i,inclusive_min:exclusive_max].read().result()
    print(f"saving slice {i}.")
    with h5.File(os.path.join(out_dir, f"zap_data_{i}.h5"), "w") as f:
        dset = f.create_dataset("data", data=block, compression="gzip")

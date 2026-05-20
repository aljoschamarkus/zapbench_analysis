import numpy as np
import tensorstore as ts
from tqdm import tqdm
import h5py as h5
from config import *
import os

out_dir = PATHS.in_data("zap_aligned_slices")
out_dir.mkdir(parents=True, exist_ok=True)

f_stim = h5.File(PATHS.in_data("zap_stimulus_turning.h5"), "r")
condition_t = f_stim["condition_t"][:]

ds = ts.open({
    'open': True,
    'driver': GS["zap_aligned"][0],
    'kvstore': GS["zap_aligned"][1],
}).result()

# for i in tqdm(np.arange(VOLUME_LIMS["z_min"], VOLUME_LIMS["z_max"], 1)):
#     if os.path.isfile(os.path.join(PATHS.in_data("zap_aligned_slices"), f"zap_data_{i}.h5")):
#         continue
#     print(f"downloading slice {i}.")
#     block = ds[VOLUME_LIMS["x_min"]:VOLUME_LIMS["x_max"],VOLUME_LIMS["y_min"]:VOLUME_LIMS["y_max"],i,condition_t[0]:condition_t[-1]+1].read().result()
#     print(f"saving slice {i}.")
#     with h5.File(os.path.join(PATHS.in_data("zap_aligned_slices"), f"zap_data_{i}.h5"), "w") as f:
#         dset = f.create_dataset("data", data=block, compression="gzip")

for i in tqdm(np.arange(VOLUME_LIMS["z_min"], VOLUME_LIMS["z_max"], 1)):
    out_file = out_dir / f"zap_data_{i}.h5"
    if out_file.is_file():
        continue

    # print(f"downloading slice {i}.")
    block = ds[
        VOLUME_LIMS["x_min"]:VOLUME_LIMS["x_max"],
        VOLUME_LIMS["y_min"]:VOLUME_LIMS["y_max"],
        i,
        condition_t[0]:condition_t[-1]+1
    ].read().result()

    # print(f"saving slice {i}.")
    with h5.File(out_file, "w") as f:
        dset = f.create_dataset("data", data=block, compression="gzip")

print("slices to volume...")

z_slices = []

for file in tqdm(sorted(PATHS.in_data("zap_aligned_slices").glob("*.h5"), key=lambda p: int(p.stem.split("_")[-1]))):
    path_str = str(file)
    print(path_str)

    f = h5.File(path_str, 'r')
    z_slice = f['data'][:,:,:]

    z_slices.append(z_slice)

data = np.array(z_slices)
print("saving volume...")
with h5.File(PATHS.in_data("zap_aligned_volume.h5"), "w") as f:
    dset = f.create_dataset("data", data=data, compression="gzip")
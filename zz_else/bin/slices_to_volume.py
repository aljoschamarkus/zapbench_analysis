import numpy as np
from tqdm import tqdm
import h5py as h5
from config import *

z_slices = []

for file in tqdm(sorted(PATHS.in_data("zapbench_aligned_slices").glob("*.h5"), key=lambda p: int(p.stem.split("_")[-1]))):
    path_str = str(file)
    print(path_str)

    f = h5.File(path_str, 'r')
    z_slice = f['data'][:,:,:]

    z_slices.append(z_slice)

data = np.array(z_slices)
print("saving volume...")
with h5.File(PATHS.in_data("zapbench_aligned_volume.h5"), "w") as f:
    dset = f.create_dataset("data", data=data, compression="gzip")
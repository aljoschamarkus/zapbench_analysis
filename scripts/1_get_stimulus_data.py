import tensorstore as ts
import numpy as np
import h5py
from config import *
import os

os.makedirs(MAIN_DIR, exist_ok=True)

ds_stim = ts.open({
    'open': True,
    'driver': 'zarr',
    'kvstore': 'gs://zapbench-release/volumes/20240930/stimuli_features'
}).result()

stim = ds_stim[:, [9, 10, 11, 12]].read().result()

condition_active = np.round(stim[:,3]).astype(int)
stim_active = np.round(stim[:,0]).astype(int)
sin_dir = np.round(stim[:,1]).astype(int)
cos_dir = np.round(stim[:,2]).astype(int)

condition_mask = condition_active == 1
stim_off_mask = stim_active == 0
stim_on_mask = stim_active == 1
forward  = stim_on_mask & (sin_dir == 0) & (cos_dir == 1)
right    = stim_on_mask & (sin_dir == 1) & (cos_dir == 0)
backward = stim_on_mask & (sin_dir == 0) & (cos_dir == -1)
left     = stim_on_mask & (sin_dir == -1) & (cos_dir == 0)

condition_t = np.where(condition_mask)[0]
stim_off_t = np.where(stim_on_mask)[0]
stim_on_t = np.where(stim_on_mask)[0]
forward_t  = np.where(forward)[0]
right_t    = np.where(right)[0]
backward_t = np.where(backward)[0]
left_t     = np.where(left)[0]

with h5py.File(STIM_FILE, "w") as f:
    f.create_dataset("condition_t", data=condition_t)
    f.create_dataset("stim_off_t", data=stim_off_t)
    f.create_dataset("stim_on_t", data=stim_on_t)
    f.create_dataset("forward_t", data=forward_t)
    f.create_dataset("right_t", data=right_t)
    f.create_dataset("backward_t", data=backward_t)
    f.create_dataset("left_t", data=left_t)
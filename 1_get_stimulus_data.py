import tensorstore as ts
import numpy as np
import pandas as pd
import h5py

ds_stim = ts.open({
    'open': True,
    'driver': 'zarr',
    'kvstore': 'gs://zapbench-release/volumes/20240930/stimuli_features'
}).result()

stim = ds_stim[3700:5100, [9, 10, 11, 12]].read().result()

stim_active = np.round(stim[:,0]).astype(int)
sin_dir = np.round(stim[:,1]).astype(int)
cos_dir = np.round(stim[:,2]).astype(int)

mask_stim_active = stim_active == 1
forward  = mask_stim_active & (sin_dir == 0)  & (cos_dir == 1)
right    = mask_stim_active & (sin_dir == 1)  & (cos_dir == 0)
backward = mask_stim_active & (sin_dir == 0)  & (cos_dir == -1)
left     = mask_stim_active & (sin_dir == -1) & (cos_dir == 0)

active_t = np.where(mask_stim_active)[0] + 3700
forward_t  = np.where(forward)[0] + 3700
right_t    = np.where(right)[0] + 3700
backward_t = np.where(backward)[0] + 3700
left_t     = np.where(left)[0] + 3700

stim_df = pd.DataFrame(
    False,
    index=np.arange(7879),
    columns=["active", "f", "r", "b", "l"]
)

stim_df.loc[active_t, "active"] = True
stim_df.loc[forward_t, "f"] = True
stim_df.loc[right_t, "r"] = True
stim_df.loc[backward_t, "b"] = True
stim_df.loc[left_t, "l"] = True

with h5py.File("/Users/aljoscha/Downloads/stim.h5", "w") as f:
    f.create_dataset("data", data=stim_df.to_numpy())
    f.create_dataset("columns", data=np.array(stim_df.columns, dtype="S"))
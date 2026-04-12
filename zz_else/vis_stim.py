import h5py as h5
from config import *
import matplotlib.pyplot as plt
import tensorstore as ts

f_stim = h5.File(STIM_H5, "r")
condition_t_full = f_stim["condition_t"][:]

start_index = condition_t_full.min()
condition_t = condition_t_full - start_index

stim_off_t = f_stim["stim_off_t"][:] - start_index
forward_t = f_stim["forward_t"][:] - start_index
right_t = f_stim["right_t"][:] - start_index
backward_t = f_stim["backward_t"][:] - start_index
left_t = f_stim["left_t"][:] - start_index

ds_stim = ts.open({
    'open': True,
    'driver': 'zarr',
    'kvstore': 'gs://zapbench-release/volumes/20240930/stimuli_features'
}).result()

stim = ds_stim[condition_t_full.min():condition_t_full.max(), [9, 10, 11, 12]].read().result()
print(stim.shape)
plt.plot(stim[:, 1], alpha=0.5, color='blue')
plt.plot(stim[:, 2], alpha=0.5, color='red')
plt.show()

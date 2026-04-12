import h5py as h5
import numpy as np
import scipy.ndimage as sciimg
from config import *
from utils import img_to_ng

f = h5.File(FUNCTIONAL_IMG_H5, "r")

z_slice_temporal = f['data'][8:11, :, :, :]
img_original = z_slice_temporal.mean(axis=3)

smoothed = sciimg.gaussian_filter(z_slice_temporal, (0, 1, 1, 0))
img_smoothed = smoothed.mean(axis=3)

# 2) z-score each pixel trace over time
mean_t = smoothed.mean(axis=3, keepdims=True)
std_t = smoothed.std(axis=3, keepdims=True) + 1e-8
zdata = (smoothed - mean_t) / std_t
# 3) local neighborhood mean trace excluding center pixel
local_mean = np.empty_like(zdata)
for t in range(zdata.shape[2]):
    local_mean[:, :, t] = sciimg.uniform_filter(zdata[:, :, t], size=7)

local_mean = (49 * local_mean - zdata) / 48

# 4) z-score neighborhood mean traces
lm_mean = local_mean.mean(axis=3, keepdims=True)
lm_std = local_mean.std(axis=3, keepdims=True) + 1e-8
local_mean_z = (local_mean - lm_mean) / lm_std

# 5) temporal correlation map
corr_map = np.mean(zdata * local_mean_z, axis=3)

with h5.File(ACTIVITY_CORRELATION_H5, "w") as f:
    dset = f.create_dataset("data", data=corr_map, compression="gzip")

print(corr_map.shape)

layers_dict = {
    "original": img_original,
    "smoothed": img_smoothed,
    "corr_map": corr_map,
}

img_to_ng(layers_dict)
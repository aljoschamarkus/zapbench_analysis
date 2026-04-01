import h5py as h5
import numpy as np
import scipy.ndimage as sciimg
import matplotlib
matplotlib.use("MacOSX")   # or TkAgg, WXAgg, MacOSX
from matplotlib import pyplot as plt

from config import *

f = h5.File(DATA_FILE, "r")

z_slice_temporal = f['data'][8, :, :, :]
img_0 = z_slice_temporal.mean(axis=2)

smoothed = sciimg.gaussian_filter(z_slice_temporal, (0.5, 0.5, 0))

img_1 = smoothed.mean(axis=2)

# 2) z-score each pixel trace over time
mean_t = smoothed.mean(axis=2, keepdims=True)
std_t = smoothed.std(axis=2, keepdims=True) + 1e-8
zdata = (smoothed - mean_t) / std_t

# 3) local neighborhood mean trace excluding center pixel
local_mean = np.empty_like(zdata)
for t in range(zdata.shape[2]):
    local_mean[:, :, t] = sciimg.uniform_filter(zdata[:, :, t], size=3)

local_mean = (9 * local_mean - zdata) / 8

# 4) z-score neighborhood mean traces
lm_mean = local_mean.mean(axis=2, keepdims=True)
lm_std = local_mean.std(axis=2, keepdims=True) + 1e-8
local_mean_z = (local_mean - lm_mean) / lm_std

# 5) temporal correlation map
corr_map = np.mean(zdata * local_mean_z, axis=2)

with h5.File(ROI_FILE, "w") as f:
    dset = f.create_dataset("data", data=corr_map, compression="gzip")

# plot test:
fig, ax = plt.subplots(1, 2)
ax[0].imshow(img_0)
ax[0].axis('off')
ax[0].set_title('original')
ax[1].imshow(corr_map)
ax[1].axis('off')
ax[1].set_title('activity correlation')

# plt.show()
plt.savefig('/Users/aljoscha/Downloads/roi_correlation_temporal.png')
plt.close()
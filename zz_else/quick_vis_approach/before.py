import h5py as h5
from config import *
import tifffile as tiff
import numpy as np
import matplotlib.pyplot as plt

# shape microscope output: (time, channel, z, y, x)
# current zap test data shape: (z, x, y, t)

data_h5 = h5.File(PATHS.in_data("zapbench_aligned_volume.h5"), "r")
data = data_h5["data"][:, :, :, :200]
print(data.shape, data.dtype)
vol = data.astype(np.float32)
z, y, x, t = vol.shape


win = 101
constant = 1e-8

# from scipy.ndimage import percentile_filter
# F0 = percentile_filter(vol, percentile=20, size=(1, 1, 1, win))
from scipy.ndimage import uniform_filter1d
F0 = uniform_filter1d(vol, size=win, axis=3, mode='nearest')
dff = (vol - F0) / (F0+constant)

vmax = np.percentile(np.abs(dff), 99)
vol_norm = np.clip(dff, -vmax, vmax)
vol_norm = (vol_norm + vmax) / (2 * vmax)

activity = np.clip(dff, 0, None)
# activity = activity ** 2
vmax2 = np.percentile(activity, 99.9)
activity = (activity - activity.min()) / (vmax2 - activity.min())

cmap = plt.get_cmap("jet")
colors = cmap(np.linspace(0, 1, z))[:, :3]

colored = activity[..., None] * colors[:, None, None, None, :]
rgb_time = colored.max(axis=0)

# activity = np.clip(dff * 2, 0, 1)
#
# colors = plt.get_cmap("hsv")(np.linspace(0, 1, z))[:, :3]
#
# colored = activity[..., None] * colors[:, None, None, None, :]
#
# rgb_time = colored.max(axis=0)

rgb_time = np.moveaxis(rgb_time, 2, 0)
rgb_time_uint8 = np.clip(rgb_time * 255, 0, 255).astype(np.uint8)

tiff.imwrite(
    PATHS.in_tiff("zapbench_aligned_volume.tiff"),
    rgb_time_uint8,
    photometric="rgb"
)
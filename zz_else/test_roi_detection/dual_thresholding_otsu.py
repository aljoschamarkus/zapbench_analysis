import h5py as h5
import numpy as np
import matplotlib
matplotlib.use("MacOSX")   # or TkAgg, WXAgg, MacOSX
import matplotlib.pyplot as plt

from config import *

f = h5.File(ACTIVITY_CORRELATION_H5, "r")
corr_map = f['data'][:,:]

from skimage.filters import threshold_otsu
from skimage.morphology import remove_small_objects
from scipy import ndimage as ndi
from skimage.feature import peak_local_max

thr = threshold_otsu(corr_map)
thr_low = 0.95 * thr
thr_high = 1.10 * thr

mask_low = corr_map > thr_low
mask_high = corr_map > thr_high

mask_low_clean = remove_small_objects(mask_low, min_size=20)
mask_high_clean = remove_small_objects(mask_high, min_size=8)

# -------------------------
# watershed on LOW threshold
# -------------------------
dist_low = ndi.distance_transform_edt(mask_low_clean)
coords_low = peak_local_max(dist_low, labels=mask_low_clean, min_distance=3)

markers_low = np.zeros_like(mask_low_clean, dtype=int)
markers_low[tuple(coords_low.T)] = np.arange(1, len(coords_low) + 1)

from skimage.segmentation import watershed
labels_low = watershed(-dist_low, markers_low, mask=mask_low_clean)

# --------------------------
# watershed on HIGH threshold
# --------------------------
dist_high = ndi.distance_transform_edt(mask_high_clean)
coords_high = peak_local_max(dist_high, labels=mask_high_clean, min_distance=3)

markers_high = np.zeros_like(mask_high_clean, dtype=int)
markers_high[tuple(coords_high.T)] = np.arange(1, len(coords_high) + 1)

labels_high = watershed(-dist_high, markers_high, mask=mask_high_clean)


fig, ax = plt.subplots(1, 4)

ax[0].imshow(corr_map, cmap="viridis")
ax[0].axis('off')
ax[0].set_title('activity correlation')

dual_mask_rgb = np.zeros((*mask_low.shape, 3), dtype=float)
dual_mask_rgb[mask_low] = [1.0, 0.0, 0.0]     # red = low threshold
dual_mask_rgb[mask_high] = [0.0, 1.0, 1.0]    # cyan = high threshold

ax[1].imshow(dual_mask_rgb)
ax[1].axis('off')
ax[1].set_title('dual thresholding')

ax[2].imshow(labels_low, cmap="nipy_spectral")
ax[2].axis('off')
ax[2].set_title('watershed permissive')

ax[3].imshow(labels_high, cmap="nipy_spectral")
ax[3].axis('off')
ax[3].set_title('watershed strict')

plt.tight_layout()
plt.show()
# plt.savefig("/Users/aljoscha/Downloads/roi_detection.png", dpi=600)
# plt.close()
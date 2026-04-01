import h5py as h5
import numpy as np
import matplotlib
matplotlib.use("MacOSX")   # or TkAgg, WXAgg, MacOSX
import scipy.ndimage as sciimg
import matplotlib.pyplot as plt

from config import *

f = h5.File(ROI_FILE, "r")
corr_map = f['data'][:,:]

from skimage.filters import threshold_otsu
from skimage.feature import peak_local_max
from skimage.morphology import remove_small_objects
from skimage.segmentation import watershed

# optional small smoothing of the correlation map itself
corr_smooth = sciimg.gaussian_filter(corr_map, sigma=0.5)
# corr_smooth = corr_map

# permissive mask for ROI extent
thr = threshold_otsu(corr_smooth)
mask = corr_smooth > (1 * thr)
mask = remove_small_objects(mask, min_size=20)

# detect local peaks directly on corr_map
coords = peak_local_max(
    corr_smooth,
    labels=mask,
    min_distance=5,
    threshold_abs=1 * thr
)

markers = np.zeros_like(mask, dtype=int)
markers[tuple(coords.T)] = np.arange(1, len(coords) + 1)

# watershed on negative correlation map:
# peaks expand outward inside the permissive mask
labels_peaks = watershed(-corr_smooth, markers, mask=mask)

fig, ax = plt.subplots(1, 3)

ax[0].imshow(corr_smooth, cmap="viridis")
if len(coords) > 0:
    ax[0].plot(coords[:, 1], coords[:, 0], 'r.', markersize=4)
ax[0].axis('off')
ax[0].set_title('original')

ax[1].imshow(mask, cmap="gray")
ax[1].axis('off')
ax[1].set_title('peak branch mask')

ax[2].imshow(labels_peaks, cmap="nipy_spectral")
ax[2].axis('off')
ax[2].set_title('peaks + watershed')
# plt.show()
plt.savefig('/Users/aljoscha/Downloads/roi_peak_detection.png')
plt.close()

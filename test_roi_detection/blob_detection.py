import h5py as h5
import numpy as np
import matplotlib
matplotlib.use("MacOSX")   # or TkAgg, WXAgg, MacOSX
import scipy.ndimage as sciimg
import matplotlib.pyplot as plt

from config import *

f = h5.File(ROI_FILE, "r")
corr_map = f['data'][:,:]

from skimage.feature import blob_log

corr_smooth = sciimg.gaussian_filter(corr_map, sigma=1)

blobs = blob_log(
    corr_smooth,
    min_sigma=3,
    max_sigma=6,
    num_sigma=6,
    threshold=0.03
)

fig2, ax2 = plt.subplots()
ax2.imshow(corr_smooth, cmap="viridis")

for blob in blobs:
    y, x, s = blob
    circ = plt.Circle((x, y), radius=np.sqrt(2) * s, color='r', fill=False, linewidth=1)
    ax2.add_patch(circ)

ax2.set_title('blob detection on activity correlation')
ax2.axis('off')
plt.show()
# plt.savefig('/Users/aljoscha/Downloads/blob_detection.png')
# plt.close()
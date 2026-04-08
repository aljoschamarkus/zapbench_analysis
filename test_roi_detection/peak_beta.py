import h5py as h5
import numpy as np
import matplotlib
matplotlib.use("MacOSX")
import matplotlib.pyplot as plt
import heapq

from config import *
from skimage.filters import threshold_otsu
from skimage.feature import peak_local_max
from skimage.morphology import remove_small_objects


# ----------------------------
# Parameters
# ----------------------------
TARGET_AREA = 100
MIN_DISTANCE = 4
ALPHA = 0.05   # penalize distance from seed
BETA = 0.1    # reward compact growthx


# ----------------------------
# Load image
# ----------------------------
with h5.File(ROI_FILE, "r") as f:
    image = f["data"][:, :]


# ----------------------------
# ROI mask
# ----------------------------
thr = threshold_otsu(image)
mask = image > thr
mask = remove_small_objects(mask, min_size=20)


# ----------------------------
# Peak detection
# ----------------------------
coords = peak_local_max(
    image,
    labels=mask,
    min_distance=MIN_DISTANCE,
    threshold_abs=thr
)


# ----------------------------
# Helper: 8-neighborhood
# ----------------------------
def neighbors(r, c, shape):
    rows, cols = shape
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < rows and 0 <= cc < cols:
                yield rr, cc


def count_region_neighbors(region, r, c):
    return sum(region[rr, cc] for rr, cc in neighbors(r, c, region.shape))


# ----------------------------
# Segment by growing blobs from peaks
# ----------------------------
def segment_from_peaks(image, seeds, mask, target_area, alpha, beta):
    """
    Grow one blob from each seed.
    Growth prefers bright pixels, but stays compact and near the seed.
    Blobs are not allowed to overlap.
    """
    label_image = np.zeros(image.shape, dtype=int)
    claimed = np.zeros(image.shape, dtype=bool)

    # strongest peaks grow first
    seeds = sorted(seeds, key=lambda rc: image[rc[0], rc[1]], reverse=True)

    for label, (sr, sc) in enumerate(seeds, start=1):
        if not mask[sr, sc] or claimed[sr, sc]:
            continue

        region = np.zeros(image.shape, dtype=bool)
        heap = []

        region[sr, sc] = True
        claimed[sr, sc] = True
        label_image[sr, sc] = label
        area = 1

        def score(r, c):
            dist = np.hypot(r - sr, c - sc)
            compactness = count_region_neighbors(region, r, c)
            return image[r, c] - alpha * dist + beta * compactness

        for rr, cc in neighbors(sr, sc, image.shape):
            if mask[rr, cc] and not claimed[rr, cc]:
                heapq.heappush(heap, (-score(rr, cc), rr, cc))

        while heap and area < target_area:
            _, r, c = heapq.heappop(heap)

            if claimed[r, c] or not mask[r, c]:
                continue

            region[r, c] = True
            claimed[r, c] = True
            label_image[r, c] = label
            area += 1

            for rr, cc in neighbors(r, c, image.shape):
                if mask[rr, cc] and not claimed[rr, cc]:
                    heapq.heappush(heap, (-score(rr, cc), rr, cc))

    return label_image


label_image = segment_from_peaks(
    image=image,
    seeds=[tuple(x) for x in coords],
    mask=mask,
    target_area=TARGET_AREA,
    alpha=ALPHA,
    beta=BETA,
)


# ----------------------------
# Plot
# ----------------------------
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

ax[0].imshow(image, cmap="viridis")
ax[0].scatter(coords[:, 1], coords[:, 0], c="red", s=20, marker="x")
ax[0].set_title("Image + peaks")
ax[0].set_axis_off()

ax[1].imshow(mask, cmap="gray")
ax[1].set_title("Mask")
ax[1].set_axis_off()

ax[2].imshow(image, cmap="gray")
ax[2].imshow(np.ma.masked_where(label_image == 0, label_image),
             cmap="nipy_spectral", alpha=0.5)
ax[2].set_title("Segmentation")
ax[2].set_axis_off()

plt.tight_layout()
plt.show()
import h5py as h5
import numpy as np
import scipy.ndimage as sciimg
from config import *
from utils import img_to_ng

f = h5.File(DATA_FILE, "r")

z_slice_temporal = f['data'][8, :, :, :]
img_original = z_slice_temporal.mean(axis=2)

smoothed = sciimg.gaussian_filter(z_slice_temporal, (1, 1, 0))
img_smoothed = smoothed.mean(axis=2)

# 2) z-score each pixel trace over time
mean_t = smoothed.mean(axis=2, keepdims=True)
std_t = smoothed.std(axis=2, keepdims=True) + 1e-8
zdata = (smoothed - mean_t) / std_t
# 3) local neighborhood mean trace excluding center pixel
local_mean = np.empty_like(zdata)
for t in range(zdata.shape[23]):
    local_mean[:, :, t] = sciimg.uniform_filter(zdata[:, :, t], size=7)

local_mean = (49 * local_mean - zdata) / 48

# 4) z-score neighborhood mean traces
lm_mean = local_mean.mean(axis=2, keepdims=True)
lm_std = local_mean.std(axis=2, keepdims=True) + 1e-8
local_mean_z = (local_mean - lm_mean) / lm_std

# 5) temporal correlation map
corr_map = np.mean(zdata * local_mean_z, axis=2)

with h5.File(ROI_FILE, "w") as f:
    dset = f.create_dataset("data", data=corr_map, compression="gzip")

print(corr_map.shape)

layers_dict = {
    "original": img_original,
    "smoothed": img_smoothed,
    "corr_map": corr_map,
}

def img_to_ng2(layers):
    import neuroglancer as ng
    from numpy import min, max
    PORT = 8080
    ng.set_server_bind_address("127.0.0.1", PORT)

    in_dimensions = ng.CoordinateSpace(
        names=["y", "x"],
        scales=[1, 1],
    )

    out_dimensions = ng.CoordinateSpace(
        names=["x", "y"],
        scales=[1, 1],
    )

    matrix = [
        [0, 1, 0],
        [1, 0, 0],
    ]

    viewer = ng.Viewer()

    with viewer.txn() as s:
        for name, img in layers.items():
            img_scaled = (img-min(img))/(max(img)-min(img))
            s.layers[name] = ng.ImageLayer(
                source=ng.LayerDataSource(
                    url=ng.LocalVolume(
                        data=img_scaled,
                        dimensions=in_dimensions,
                    ),
                    transform=ng.CoordinateSpaceTransform(
                    matrix=matrix,
                    output_dimensions=out_dimensions,
                    )
                )
            )

        s.layout = "xy"

    print(viewer)
    input("stop server...")

img_to_ng2(layers_dict)
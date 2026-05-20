import h5py as h5
from config import *
import tifffile as tiff
import numpy as np

data_h5 = h5.File(PATHS.in_data("zapbench_aligned_volume.h5"), "r")
data = data_h5["data"][:, :, :, 200]
print(data.shape, data.dtype)
print(data.min(), data.max(), data.dtype)

data_norm = (data - data.min()) / (data.max() - data.min())

data_uint16 = (data_norm * 65535).astype(np.uint16)

tiff.imwrite(
    PATHS.in_tiff("zapbench_aligned_volume.tiff"),
    data_uint16,
)

data_transposed = np.transpose(data_uint16, (1, 2, 0))
print(data.shape)


import neuroglancer as ng
dimensions = ng.CoordinateSpace(
    names=["x", "y", "z"],
    units=["nm", "nm", "nm"],
    scales=[406, 406, 4000],
)

PORT = 8080

ng.set_server_bind_address("127.0.0.1", PORT)

viewer = ng.Viewer()

with viewer.txn() as s:

    s.layers["vol"] = ng.ImageLayer(
        source=ng.LayerDataSource(
            url=ng.LocalVolume(
                data=data_transposed,
                dimensions=dimensions,
                volume_type="image",
            ),
        ),
    )

print(viewer)

input("stop server...")



# window = 101
# dff = dff(data, window)

# activity_max = np.percentile(np.abs(dff), 99)
# vol_norm = np.clip(dff, -activity_max, activity_max)
#
# rgb_time = np.moveaxis(data, 2, 0)
import tensorstore as ts
import numpy as np
from config import *
import scipy.ndimage as sciimg
import tifffile

# "gs://zapbench-release/volumes/20240930/segmentation_xy_multiscale/|zarr3:"
ds = {
    'open': True,
    'driver': 'zarr3',
    'kvstore': "gs://zapbench-release/volumes/20240930/segmentation_xy"
}

ds_ts = ts.open(ds, open=True).result()
ds_subsample = ds_ts[:, :, :].read().result()

# ds_dilated = sciimg.binary_dilation(ds_subsample, axes=(0, 1))
footprint = np.array([
    [0,1,0],
    [1,1,1],
    [0,1,0]
], dtype=bool)
ds_dilated = sciimg.grey_dilation(ds_subsample, footprint=footprint, axes=(0, 1))

ds_substracted = ds_subsample - ds_dilated
ds_binary = (ds_substracted != 0).astype(np.uint32)

ds_transposed = np.transpose(ds_binary, (2, 0, 1)) # (z, y, x, rgb)

mask_mike = tifffile.imread(DS_MASK_MIKE)
mask_mike_flipped = np.flip(mask_mike, axis=2)

mask = ds_transposed.astype(bool)
mask_mike_flipped[mask] = [255, 255, 255]

tifffile.imwrite(DS_MASK_ZAP_ID_OUTLINE, mask_mike_flipped)
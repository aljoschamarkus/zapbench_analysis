import tensorstore as ts
import numpy as np
import h5py as h5
import scipy.ndimage as sciimg
from config import *

ds_segments = ts.open({
    'open': True,
    'driver': GS["zap_segmentation"][0],
    'kvstore': GS["zap_segmentation"][1],
}).result()

footprint = np.array([
    [0,1,0],
    [1,1,1],
    [0,1,0]
], dtype=bool)

ds_dilated = sciimg.grey_dilation(ds_segments, footprint=footprint, axes=(0, 1))
ds_subtracted = ds_segments - ds_dilated
ds_scaled = (ds_subtracted - np.min(ds_subtracted)) / (np.max(ds_subtracted) - np.min(ds_subtracted))
zap_outlines = (ds_scaled != 0).astype(np.uint32)

with h5.File(PATHS.in_data("zap_segments.h5") , "w") as f:
    f.create_dataset("segments", data=ds_segments, compression="gzip")
    f.create_dataset("outlines", data=zap_outlines, compression="gzip")
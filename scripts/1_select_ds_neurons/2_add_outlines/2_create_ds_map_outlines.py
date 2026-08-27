import numpy as np
from config import *
import tifffile
import h5py as h5

f_stim = h5.File(PATHS.in_data("zap_segmentation.h5"), "r")
outlines = f_stim["outlines"][:]

ds_map = None
if PATHS.in_tiff("ds_map.tif").exists():
    outlines_transposed = np.transpose(outlines, (2, 1, 0)) # (z, y, x, rgb)
    ds_map = tifffile.imread(PATHS.in_tiff("ds_map.tif"))
    mask = outlines_transposed.astype(bool)
    ds_map[mask] = [255, 255, 255]
    tifffile.imwrite(PATHS.in_tiff("ds_map_outlines.tif"), ds_map)

colormapbigfull = None
if PATHS.in_tiff("colormapbigfull.tif").exists():
    outlines_transposed = np.transpose(outlines, (2, 0, 1)) # (z, y, x, rgb)
    outlines_flipped = np.flip(outlines_transposed, axis=2)
    mask_mike = tifffile.imread(PATHS.in_tiff("colormapbigfull.tif"))
    mask = outlines_flipped.astype(bool)
    mask_mike[mask] = [255, 255, 255]
    tifffile.imwrite(PATHS.in_tiff("colormapbigfull_outlines.tif"), mask_mike)
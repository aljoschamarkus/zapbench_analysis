import numpy as np
import tifffile as tiff
from config import *
from utils import *

condition_t, list_conditions = stimulus_indices(STIM_FILE)

vector_x, vector_y = ds_vectors(path=DATA_FILE, t_axis=3, condition_t=condition_t, list_conditions=list_conditions)

rgb_block = vector_to_rgb(vector_x, vector_y, threshold=99)
rgb_block_transposed = np.transpose(rgb_block, (0, 2, 1, 3)) # (z, y, x, rgb)
rgb_block_final = (255 * np.clip(rgb_block_transposed, 0, 1)).astype(np.uint8)

d_shape = data_shape("z", "y", "x", "t") # (z, y, x, t)
tiff_shape = (d_shape[0], d_shape[1], d_shape[2], 3) # (z, y, x, rgb) -> (72, 1328, 2048, 3)
vol = np.zeros(tiff_shape, dtype=np.uint8)

vol[
    VOLUME_LIMS["z_min"]:VOLUME_LIMS["z_max"],
    VOLUME_LIMS["y_min"]:VOLUME_LIMS["y_max"],
    VOLUME_LIMS["x_min"]:VOLUME_LIMS["x_max"],
    :
] = rgb_block_final

tiff.imwrite(TIF_FILE, vol)
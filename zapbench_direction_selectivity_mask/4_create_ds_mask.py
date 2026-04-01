import numpy as np
from tqdm import tqdm
import h5py as h5
import tifffile as tiff
from config import *
from utils import *

f_stim = h5.File(STIM_FILE, "r")

condition_t_full = f_stim["condition_t"][:]
start_index = condition_t_full.min()
condition_t = condition_t_full - start_index

stim_off_t = f_stim["stim_off_t"][:] - start_index
stim_on_t = f_stim["stim_on_t"][:] - start_index
forward_t = f_stim["forward_t"][:] - start_index
right_t = f_stim["right_t"][:] - start_index
backward_t = f_stim["backward_t"][:] - start_index
left_t = f_stim["left_t"][:] - start_index

list_conditions = [stim_on_t, forward_t, right_t, backward_t, left_t]

f_data = h5.File(DATA_FILE, "r")
data = f_data["data"]

n_t = data.shape[3]
condition_t_valid = condition_t[(condition_t >= 0) & (condition_t < n_t)]
vols_off = data[:, :, :, condition_t_valid]
background_off = vols_off.mean(axis=3)

stimuli = []
for cond_t in tqdm(list_conditions):
    cond_t = cond_t[(cond_t >= 0) & (cond_t < n_t)]
    data_t = data[:, :, :, cond_t]
    data_mean = data_t.mean(axis=3)
    img_bs = data_mean - background_off
    stimuli.append(img_bs)

stimuli_np = np.array(stimuli)

vector_x = stimuli[1] - stimuli[3]
vector_y = stimuli[2] - stimuli[4]

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
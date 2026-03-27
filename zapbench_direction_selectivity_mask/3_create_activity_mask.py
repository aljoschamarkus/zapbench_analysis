import numpy as np
from pathlib import Path
from tqdm import tqdm
import h5py as h5
import tifffile as tiff
from config import *
from utils import vector_to_rgb

f_stim = h5.File(STIM_FILE, "r")

condition_t_full = f_stim["condition_t"][:-2]
start_index = condition_t_full.min()
condition_t = condition_t_full - start_index
print(condition_t.shape)

stim_off_t = f_stim["stim_off_t"][:] - start_index
stim_on_t = f_stim["stim_on_t"][:] - start_index
forward_t = f_stim["forward_t"][:] - start_index
right_t = f_stim["right_t"][:] - start_index
backward_t = f_stim["backward_t"][:] - start_index
left_t = f_stim["left_t"][:] - start_index

list_conditions = [stim_on_t, forward_t, right_t, backward_t, left_t]

z_slices = []

for file in tqdm(sorted(Path(DATA_DIR).glob("*.h5"), key=lambda p: int(p.stem.split("_")[-1]))):
    path_str = str(file)
    print(path_str)

    f = h5.File(path_str, 'r')
    imgs = f['data'][:,:,:]
    n_t = imgs.shape[2]

    condition_t_valid = condition_t[(condition_t >= 0) & (condition_t < n_t)]
    imgs_off = imgs[:, :, condition_t_valid]
    img_0 = imgs_off.mean(axis=2)

    stimuli = []

    for cond_t in list_conditions:
        cond_t = cond_t[(cond_t >= 0) & (cond_t < n_t)]
        imgs_t = imgs[:, :, cond_t]
        img_mean = imgs_t.mean(axis=2)
        img_bs = img_mean - img_0
        stimuli.append(img_bs)

    vector_x = stimuli[1] - stimuli[3]
    vector_y = stimuli[2] - stimuli[4]

    # function in utils
    rgb_matrix = vector_to_rgb(vector_x, vector_y, threshold=99.5)
    z_slices.append(rgb_matrix)

# create tif volume
vol = np.zeros((72, 1328, 2048, 3), dtype=np.uint8)
rgb_block = np.stack(
    [img.transpose(1, 0, 2) for img in z_slices],
    axis=0
)
rgb_block = (255 * np.clip(rgb_block, 0, 1)).astype(np.uint8)
vol[
    VOLUME_LIMS["z_min"]:VOLUME_LIMS["z_max"],
    VOLUME_LIMS["y_min"]:VOLUME_LIMS["y_max"],
    VOLUME_LIMS["x_min"]:VOLUME_LIMS["x_max"],
    :
] = rgb_block

tiff.imwrite(TIF_FILE, vol)
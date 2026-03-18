import h5py as h5
import numpy as np
import utils
from matplotlib.colors import hsv_to_rgb
from pathlib import Path
import tifffile as tiff
from tqdm import tqdm

dir_path = Path("/Users/aljoscha/Downloads/zapbench_aligned")

condition_name = 'turning'
inclusive_min, exclusive_max = utils.get_condition_bounds(condition_name)

f_stim = h5.File("/Users/aljoscha/Downloads/stim.h5", "r")
stim = f_stim['data'][inclusive_min:exclusive_max, :]

z_slices = []

for file in tqdm(sorted(dir_path.glob("*.h5"))):
    path_str = str(file)
    print(path_str)
    f = h5.File(path_str, 'r')

    imgs = f['data'][:,:,:]

    stim_off_t = np.where(stim[:, 0]==0)[0]
    imgs_off  = imgs[:, :, stim_off_t]
    img_0 = imgs_off.mean(axis=2)

    stimuli = [] # 0=stim on, 1=forward, 2=right, 3=backwards, 4=left

    for i in range(stim.shape[1]):
        stim_t = np.where(stim[:, i] == 1)[0]
        imgs_t = imgs[:, :, stim_t]
        img_mean = imgs_t.mean(axis=2)
        img_bs = img_mean - img_0
        stimuli.append(img_bs)

    vx = stimuli[1] - stimuli[3]
    vy = stimuli[2] - stimuli[4]

    def vector_to_rgb(vx, vy):
        # outliner insensitive colormap scaling
        mag = np.maximum(np.abs(vx), np.abs(vy))
        scale = np.percentile(mag, 99)
        vx / (scale + 1e-6), vy / (scale + 1e-6)
        hue = (np.arctan2(vy, vx) / (2 * np.pi)) % 1.0
        val = np.maximum(np.abs(vx), np.abs(vy))
        val = np.clip(val, 0, 1)
        sat = np.ones_like(val)
        hsv = np.stack([hue, sat, val], axis=-1)
        rgb = hsv_to_rgb(hsv)
        return rgb

    rgb = vector_to_rgb(vx, vy)
    z_slices.append(rgb)

x_lim = [700, 951]
y_lim = [450, 851]
z_lim = [15, 36]

# create tif volume
vol = np.zeros((72, 1328, 2048, 3), dtype=np.uint8)
rgb_block = np.stack(
    [img.transpose(1, 0, 2) for img in z_slices],
    axis=0
)
rgb_block = (255 * np.clip(rgb_block, 0, 1)).astype(np.uint8)
vol[
    z_lim[0]:z_lim[1],
    y_lim[0]:y_lim[1],
    x_lim[0]:x_lim[1],
    :
] = rgb_block

tiff.imwrite("/Users/aljoscha/Downloads/output_rgb_volume.tif", vol)
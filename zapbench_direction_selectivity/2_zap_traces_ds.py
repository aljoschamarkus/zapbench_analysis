import numpy as np
import h5py as h5
from config import *
from utils import *

condition_t, list_conditions = stimulus_indices(path=STIM_H5)

vector_x, vector_y = ds_vectors(path=TRACES_H5, t_axis=0, condition_t=condition_t, list_conditions=list_conditions)

vectors = np.column_stack((vector_x, vector_y))
print(vectors.shape)
print(vectors)

rgb_pre = vector_to_rgb(vector_x, vector_y, threshold=97)
rgb = (255 * rgb_pre).astype(np.uint8)

with h5.File(ZAP_DS_H5, "w") as f:
    f.create_dataset("vectors", data=vectors, compression="gzip")
    f.create_dataset("rgb", data=rgb, compression="gzip")


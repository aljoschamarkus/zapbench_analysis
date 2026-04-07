import numpy as np
import h5py as h5
from config import *
from utils import *

condition_t, list_conditions = stimulus_indices(path=STIM_FILE)

vector_x, vector_y = ds_vectors(path=TRACES_FILE, t_axis=0, condition_t=condition_t, list_conditions=list_conditions)

vectors = np.column_stack((vector_x, vector_y))

rgb_pre = vector_to_rgb(vector_x, vector_y, threshold=97)
rgb = (255 * rgb_pre).astype(np.uint8)

with h5.File(ZAP_DS, "w") as f:
    f.create_dataset("vectors", data=vectors, compression="gzip")
    f.create_dataset("rgb", data=rgb, compression="gzip")

# # Test
# IDs = [21484, 21513, 8999, 8925, 21506, 19806, 21452, 21508]
# for id in IDs:
#     print(id, rgb[id-1])

# # Read example
# ds_data = h5.File(ZAP_DS, "r")
# ds_vectors = ds_data["vectors"]
# ds_rgb = ds_data["rgb"]

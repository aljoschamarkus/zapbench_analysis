import numpy as np
import h5py as h5
from config import *
from utils import *

condition_t, list_conditions = stimulus_indices(path=PATHS.in_data("zap_stimulus_turning.h5"))

vector_x, vector_y = ds_vectors(path=PATHS.in_data("zap_traces.h5"), t_axis=0, stim_off_t=condition_t, list_conditions=list_conditions)

vectors = np.column_stack((vector_x, vector_y))

angles = np.arctan2(vector_x, vector_y) % (2 * np.pi)

u, v = square_to_circ(vector_x, vector_y)

vectors_scaled = np.column_stack((u, v))

magnitude = np.linalg.norm(vectors_scaled, axis=1)

hex_colors = np.array(
    [hex_color(vx, vy) for vx, vy in zip(vector_x, vector_y)],
    dtype="S7",
)

with h5.File(PATHS.in_data("zap_direction_selectivity.h5"), "w") as f:
    f.create_dataset("vectors", data=vectors, compression="gzip")
    f.create_dataset("angles", data=angles, compression="gzip")
    f.create_dataset("vectors_scaled", data=vectors_scaled, compression="gzip")
    f.create_dataset("hex_color", data=hex_colors, compression="gzip")
    f.create_dataset("magnitude", data=magnitude, compression="gzip")


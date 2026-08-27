import numpy as np
import h5py as h5
from config import *
from utils import *
from matplotlib.colors import hsv_to_rgb, to_hex

condition_t, list_conditions = stimulus_indices(path=PATHS.in_data("zap_stimulus_turning.h5"))

vector_x, vector_y = ds_vectors(path=PATHS.in_data("zap_traces.h5"), t_axis=0, stim_off_t=condition_t, list_conditions=list_conditions)

vectors = np.column_stack((vector_x, vector_y))

x = np.asarray(vector_x, dtype=float)
y = np.asarray(vector_y, dtype=float)

valid = ~np.isnan(x) & ~np.isnan(y)
zero = valid & (x == 0) & (y == 0)

nonzero = valid & ~zero

u = np.full_like(x, np.nan, dtype=float)
v = np.full_like(y, np.nan, dtype=float)

angle = np.full_like(x, np.nan, dtype=float)
angle[nonzero] = np.arctan2(y[nonzero], x[nonzero])

r = np.full_like(x, np.nan, dtype=float)
r[nonzero] = np.maximum(np.abs(x[nonzero]), np.abs(y[nonzero]))
r[zero] = 0.0

u[nonzero] = r[nonzero] * np.cos(angle[nonzero])
v[nonzero] = r[nonzero] * np.sin(angle[nonzero])
u[zero] = 0.0
v[zero] = 0.0

vectors_scaled = np.column_stack((u, v))

magnitude = np.linalg.norm(vectors_scaled, axis=1)

hue = np.full_like(x, np.nan, dtype=float)
hue[nonzero] = ((angle[nonzero] % (2 * np.pi)) / (2 * np.pi) + 2 / 6) % 1.0

hsv = np.stack(
    [
        np.nan_to_num(hue, nan=0.0),
        np.ones_like(hue),
        np.ones_like(hue),
    ],
    axis=1,
)

rgb = hsv_to_rgb(hsv)
hex_colors = np.array([to_hex(c) for c in rgb], dtype="S7")

hex_colors[zero] = b"#000000"
hex_colors[~valid] = b"#808080"

with h5.File(PATHS.in_data("zap_direction_selectivity.h5"), "w") as f:
    f.create_dataset("vectors", data=vectors, compression="gzip")
    f.create_dataset("vectors_scaled", data=vectors_scaled, compression="gzip")
    f.create_dataset("hex_color", data=hex_colors, compression="gzip")
    f.create_dataset("magnitude", data=magnitude, compression="gzip")


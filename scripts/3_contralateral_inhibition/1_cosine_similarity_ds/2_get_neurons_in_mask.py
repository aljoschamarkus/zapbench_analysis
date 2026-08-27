import neuprint as neu
import h5py as h5
from private import AUTH_TOKEN
from config import *
from fishfuncem.em.NeuprintServer import NeuprintServer
import numpy as np
import os

mece_data = h5.File(PATHS.in_data("zap_mece_pretectum.h5"), "r")
pretectum_coords = mece_data["pretectum"]
mask_pretectum = mece_data["mask_pretectum"][:]

vol_limits_keys = [["x_min", "x_max"], ["y_min", "y_max"], ["z_min", "z_max"]]
volume_limits = {}

scalar = 32
for i, dims in enumerate(vol_limits_keys):
    dim_min = pretectum_coords[i].min() * scalar
    dim_max = pretectum_coords[i].max() * scalar
    volume_limits.update({dims[0]: dim_min, dims[1]: dim_max})

print(volume_limits)

os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')
nps = NeuprintServer()

query = f"""
    MATCH (n:Neuron)
    WHERE n.somaLocation IS NOT NULL
      AND n.somaLocation.x >= {volume_limits["x_min"]} AND n.somaLocation.x <= {volume_limits["x_max"]}
      AND n.somaLocation.y >= {volume_limits["y_min"]} AND n.somaLocation.y <= {volume_limits["y_max"]}
      AND n.somaLocation.z >= {volume_limits["z_min"]} AND n.somaLocation.z <= {volume_limits["z_max"]}
    RETURN n.bodyId AS bodyId,
           n.zapbenchId AS zap_id,
           n.somaLocation.x AS x,
           n.somaLocation.y AS y,
           n.somaLocation.z AS z
"""
somas_in_bounding_box = neu.fetch_custom(query)
print(somas_in_bounding_box.shape)
# mask_zap_exists = somas_in_bounding_box["zap_id"].notna()
# zap_exists_df = somas_in_bounding_box.loc[mask_zap_exists].copy()
zap_exists_df = somas_in_bounding_box
# zap_exists_df["zap_id"] = zap_exists_df["zap_id"].astype(int)
print(zap_exists_df.shape)

## Map neuron coordinates back to mask voxel coordinates
zap_exists_df["x_mask"] = np.floor(zap_exists_df["x"] / scalar).astype(int)
zap_exists_df["y_mask"] = np.floor(zap_exists_df["y"] / scalar).astype(int)
zap_exists_df["z_mask"] = np.floor(zap_exists_df["z"] / scalar).astype(int)

# Keep only rows that fall inside the mask bounds
valid = (
    (zap_exists_df["x_mask"] >= 0) & (zap_exists_df["x_mask"] < mask_pretectum.shape[0]) &
    (zap_exists_df["y_mask"] >= 0) & (zap_exists_df["y_mask"] < mask_pretectum.shape[1]) &
    (zap_exists_df["z_mask"] >= 0) & (zap_exists_df["z_mask"] < mask_pretectum.shape[2])
)

zap_exists_df = zap_exists_df.loc[valid].copy()
print(zap_exists_df.shape)

# Test mask membership
x_idx = zap_exists_df["x_mask"].to_numpy()
y_idx = zap_exists_df["y_mask"].to_numpy()
z_idx = zap_exists_df["z_mask"].to_numpy()

in_pretectum = mask_pretectum[x_idx, y_idx, z_idx].astype(bool)

zap_exists_df["area"] = np.select(
    [in_pretectum],
    ["pretectum"],
    default=None
)

zap_exists_df = zap_exists_df[zap_exists_df["area"].notna()].copy()
zap_exists_df = zap_exists_df.drop(columns=["x_mask", "y_mask", "z_mask", "x", "y", "z", "area"])
print(zap_exists_df.shape)
zap_exists_df.to_csv(PATHS.in_data("neurons_pretectum.csv"), index=False)
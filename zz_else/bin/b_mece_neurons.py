import neuprint as neu
import h5py as h5
from private import AUTH_TOKEN
from config import *
from utils import *
from fishfuncem.em.NeuprintServer import NeuprintServer
import numpy as np
import pandas as pd

mece_data = h5.File(MECE_MASKS_H5, "r")
thalamus_coords = mece_data["thalamus"]
pretectum_coords = mece_data["pretectum"]
mask_pretectum = mece_data["mask_pretectum"][:]
mask_thalamus = mece_data["mask_thalamus"][:]
print(mask_pretectum.shape)

vol_limits_keys = [["x_min", "x_max"], ["y_min", "y_max"], ["z_min", "z_max"]]
volume_limits = {}

scalar = 32
for i, dims in enumerate(vol_limits_keys):
    dim_min = min(thalamus_coords[i].min(), pretectum_coords[i].min()) * scalar
    dim_max = max(thalamus_coords[i].max(), pretectum_coords[i].max()) * scalar
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
mask_zap_exists = somas_in_bounding_box["zap_id"].notna()
zap_exists_df = somas_in_bounding_box.loc[mask_zap_exists].copy()
zap_exists_df["zap_id"] = zap_exists_df["zap_id"].astype(int)
print(zap_exists_df.shape)

## Map neuron coordinates back to mask voxel coordinates
zap_exists_df["x_mask"] = np.floor(zap_exists_df["x"] / scalar).astype(int)
zap_exists_df["y_mask"] = np.floor(zap_exists_df["y"] / scalar).astype(int)
zap_exists_df["z_mask"] = np.floor(zap_exists_df["z"] / scalar).astype(int)

# Keep only rows that fall inside the mask bounds
valid = (
    (zap_exists_df["x_mask"] >= 0) & (zap_exists_df["x_mask"] < mask_thalamus.shape[0]) &
    (zap_exists_df["y_mask"] >= 0) & (zap_exists_df["y_mask"] < mask_thalamus.shape[1]) &
    (zap_exists_df["z_mask"] >= 0) & (zap_exists_df["z_mask"] < mask_thalamus.shape[2])
)

zap_exists_df = zap_exists_df.loc[valid].copy()
print(zap_exists_df.shape)

# Test mask membership
x_idx = zap_exists_df["x_mask"].to_numpy()
y_idx = zap_exists_df["y_mask"].to_numpy()
z_idx = zap_exists_df["z_mask"].to_numpy()

in_thalamus = mask_thalamus[x_idx, y_idx, z_idx].astype(bool)
in_pretectum = mask_pretectum[x_idx, y_idx, z_idx].astype(bool)

# Add area label
zap_exists_df["area"] = np.select(
    [in_thalamus & ~in_pretectum,
     in_pretectum & ~in_thalamus],
    ["thalamus", "pretectum"],
    default=None
)

zap_exists_df = zap_exists_df[zap_exists_df["area"].notna()].copy()
zap_exists_df = zap_exists_df.drop(columns=["x_mask", "y_mask", "z_mask"])
print(zap_exists_df.shape)
# zap_exists_df.to_csv(MECE_NEURONS_CSV, index=False)

df_neurons_info = nps.get_custom_neuron_list(zap_exists_df["bodyId"].tolist())

df_neurons = (
    zap_exists_df.merge(
        df_neurons_info[["bodyId", "side"]],
        on="bodyId",
        how="left"
    )
    .copy()
)

ds_data = h5.File(ZAP_DS_H5, "r")
ds_vectors = ds_data["vectors"]

df_neurons["x_vec"] = [ds_vectors[zap - 1][0] for zap in df_neurons["zap_id"]]
df_neurons["y_vec"] = [ds_vectors[zap - 1][1] for zap in df_neurons["zap_id"]]

sector_info = [hex_color(x, y) for x, y in zip(df_neurons["x_vec"], df_neurons["y_vec"])]
df_neurons["color"] = [x for x in sector_info]

def square_to_circle(x, y):
    if x == 0 and y == 0:
        return 0.0, 0.0

    if abs(x) > abs(y):
        r = x
        theta = (np.pi/4) * (y/x) if x != 0 else 0
    else:
        r = y
        theta = (np.pi/2) - (np.pi/4) * (x/y) if y != 0 else np.pi/2

    u = r * np.cos(theta)
    v = r * np.sin(theta)
    return u, v

x_scaled, y_scaled = zip(*[
    square_to_circle(x, y) if pd.notna(x) and pd.notna(y) else (np.nan, np.nan)
    for x, y in zip(df_neurons["x_vec"], df_neurons["y_vec"])
])

df_neurons["x_scaled"] = x_scaled
df_neurons["y_scaled"] = y_scaled

df_neurons["magnitude_scaled"] = np.sqrt(
    df_neurons["x_scaled"]**2 + df_neurons["y_scaled"]**2
)

threshold_pct = 85
threshold_value = df_neurons["magnitude_scaled"].quantile(threshold_pct / 100)

df_neurons.loc[df_neurons["magnitude_scaled"] >= threshold_value, "color"] = "#dbd9d9"
# df_kept = df_neurons[df_neurons["magnitude_scaled"] >= threshold_value].copy()


# df_kept.to_csv(MECE_NEURONS_CSV)
janelia_neuroglancer(df_neurons)
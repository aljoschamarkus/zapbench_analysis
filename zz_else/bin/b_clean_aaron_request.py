import neuprint as neu
import h5py as h5
from private import AUTH_TOKEN
from utils import *
from fishfuncem.em.NeuprintServer import NeuprintServer
import numpy as np
import pandas as pd

mece_data = h5.File(MECE_MASKS_H5, "r")
pretectum_coords = mece_data["pretectum"]
mask_pretectum = mece_data["mask_pretectum"][:]
print(mask_pretectum.shape)

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
mask_zap_exists = somas_in_bounding_box["zap_id"].notna()
zap_exists_df = somas_in_bounding_box.loc[mask_zap_exists].copy()
zap_exists_df["zap_id"] = zap_exists_df["zap_id"].astype(int)
print(zap_exists_df.shape)

# neuron coordinates to mask voxel coordinates
zap_exists_df["x_mask"] = np.floor(zap_exists_df["x"] / scalar).astype(int)
zap_exists_df["y_mask"] = np.floor(zap_exists_df["y"] / scalar).astype(int)
zap_exists_df["z_mask"] = np.floor(zap_exists_df["z"] / scalar).astype(int)

# rows in mask bounds
valid = (
    (zap_exists_df["x_mask"] >= 0) & (zap_exists_df["x_mask"] < mask_pretectum.shape[0]) &
    (zap_exists_df["y_mask"] >= 0) & (zap_exists_df["y_mask"] < mask_pretectum.shape[1]) &
    (zap_exists_df["z_mask"] >= 0) & (zap_exists_df["z_mask"] < mask_pretectum.shape[2])
)

zap_exists_df = zap_exists_df.loc[valid].copy()
print(zap_exists_df.shape)

# in mask
x_idx = zap_exists_df["x_mask"].to_numpy()
y_idx = zap_exists_df["y_mask"].to_numpy()
z_idx = zap_exists_df["z_mask"].to_numpy()

in_pretectum = mask_pretectum[x_idx, y_idx, z_idx].astype(bool)

zap_exists_df["area"] = np.select([in_pretectum], ["pretectum"], default=None)

zap_exists_df = zap_exists_df[zap_exists_df["area"].notna()].copy()
zap_exists_df = zap_exists_df.drop(columns=["x_mask", "y_mask", "z_mask"])
print(zap_exists_df.shape)

df_neurons_info = nps.get_custom_neuron_list(zap_exists_df["bodyId"].tolist())

df_neurons = (
    zap_exists_df.merge(
        df_neurons_info[["bodyId", "side"]],
        on="bodyId",
        how="left"
    )
    .copy()
)

aarons = pd.read_csv("/Users/aljoscha/Downloads/some_inputs_to_cluster18.csv")
df_kept = df_neurons[df_neurons["bodyId"].isin(aarons["bodyId"])]

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

aarons = pd.read_csv("/Users/aljoscha/Downloads/some_inputs_to_cluster18.csv")

# list1 = [100013117, 100015976, 100018241, 100018549, 100026999, 100034389, 100037100, 100039278, 100039958, 100054806, 100056467, 100059177, 100085638, 100091865, 100099154, 100125800, 100126848, 100138611, 100140196, 100143455, 100155835, 100157267, 100181130, 100192486, 100199341, 100208392, 100209243, 100226345, 100228700, 100234061, 100241488, 100253245, 100258611, 100301704, 100314647, 100321027, 100322660, 100328422, 100351651, 100367123, 100376698, 100381388, 100382455, 100397785, 100428018, 100434460, 100438043, 100450818, 100457380, 100460247, 100465917, 100473415, 100495025, 100536334, 100553212, 100578412, 100624099, 100632159, 100643063, 100643432, 100716026, 100718678, 100743269, 100752663, 100775796, 100780009, 100862499, 100864562, 100867643, 100878744, 100947297, 100950759, 100953047, 100959147, 100962236, 101030748, 101053151, 101059824, 101060052, 101062417, 101064034, 101076587, 101098855, 101113924, 101117474, 101119155, 101120725, 101120862, 101325524, 101367817, 101370321, 101393121, 101415343, 101433180, 101433892, 101517185, 101607941, 101610524, 101619502, 101633045, 101699479, 101711102, 101716089, 101753814, 101757941, 101791390, 101814337, 101816405, 101832684, 101835922, 101852021, 101854697, 101862389, 101868897, 101947648, 101959555, 101986860, 101987131, 102055569, 102069412, 102071079, 102108453, 102199965, 102262001, 102265364, 102298553, 102303151, 102354940, 102382343, 102410002, 102428374, 102512737, 102674903, 102708644, 102712441, 102768924, 102775960, 102783214, 102822361, 102830942, 102943975, 102973939, 103058122, 103178087, 103220028, 103240577, 103265607, 103396512, 103438451, 103456689, 103573177, 103759237, 103763514, 103809133, 103982181, 104060367, 104262441, 104426090, 104450133, 104522993, 104540242, 104564545, 104678622, 104752436, 104767447, 104858102, 104862678, 104880695, 105071628, 105145250, 105320406, 105331858, 105387150, 105410976, 105429058, 105512168, 105621301, 105719139, 105807430, 105823810, 106027059, 106125193, 106303807, 106523166, 106651957, 106949592, 107357838, 107496217, 107539587, 107592492, 107760914, 108022447, 108027319, 108439721, 109467120, 109795528, 109817938, 109924622, 110017373, 110380081, 111049338, 111195135, 111819072, 112492955, 112603947, 112609337, 113295497, 113427382, 113694954, 113949630, 114115879, 115284831, 115361281, 119015905, 121361293, 123210472, 124060058, 127368769, 127979687, 129683201, 130888005, 131513442, 140831523, 143994686, 144960536, 148741521, 149256325, 150773288, 160509969, 205190774, 417759466, 417775459, 417848971]

df_kept = df_neurons[df_neurons["bodyId"].isin(aarons["bodyId"])]
# df_kept = df_neurons[df_neurons["bodyId"].isin(list1)]
df_kept.to_csv("/Users/aljoscha/Downloads/zapbench_data_thalamus/ds_neurons2.csv")
print(df_kept.shape, df_kept.columns)
janelia_neuroglancer(df_kept)
import tensorstore as ts
import numpy as np
import pandas as pd
from config import *
import requests
from io import StringIO

# read in google sheet
r = requests.get(url_fish1_pretectal)
r.raise_for_status()

df_read = pd.read_csv(StringIO(r.text))

# read soma ids
soma_ids = np.array(df_read["id"].tolist())

# read soma locations
locations = df_read["soma_location"].values
ints = np.array([list(map(int, row.split(','))) for row in locations])
mins = ints.min(axis=0)
maxs = ints.max(axis=0)

# create bounding box
xy_scale_ng = 8 #nm
z_scale_ng = 30 #nm
xy_scale_source = 512 #nm
z_scale_source = 30 #nm
bounding_box_extension = 4000 #nm

x_min_em = int(mins[0] - bounding_box_extension / xy_scale_ng)
x_max_em = int(maxs[0] + bounding_box_extension / xy_scale_ng)
y_min_em = int(mins[1] - bounding_box_extension / xy_scale_ng)
y_max_em = int(maxs[1] + bounding_box_extension / xy_scale_ng)
z_min_em = int(mins[2] - bounding_box_extension / z_scale_ng)
z_max_em = int(maxs[2] + bounding_box_extension / z_scale_ng)

conversion_factor_xy = xy_scale_ng/xy_scale_source

x_min = round(x_min_em * conversion_factor_xy)
x_max = round(x_max_em * conversion_factor_xy)

y_min = round(y_min_em * conversion_factor_xy)
y_max = round(y_max_em * conversion_factor_xy)

z_min = z_min_em
z_max = z_max_em

print(x_min, x_max, y_min, y_max, z_min, z_max)

ds_confocal = ts.open({
    'open': True,
    'driver': GS["fish1_nt"][0],
    'kvstore': GS["fish1_nt"][1]
}).result()

ds_somas = ts.open({
    'open': True,
    'driver': GS["fish1_somas"][0],
    'kvstore': GS["fish1_somas"][1]
}).result()

region = ds_somas[x_min:x_max, y_min:y_max, z_min:z_max, 0].read().result()

mask = np.isin(region, soma_ids)

positions = np.argwhere(mask)

positions_abs = positions + np.array([x_min, y_min, z_min])
coords = positions_abs.T

matched_ids = region[mask].ravel()

vals = ds_confocal[
    coords[0],
    coords[1],
    coords[2],
    :
].read().result()

vals = np.asarray(vals)
matched_ids = np.asarray(matched_ids).ravel()

df = pd.DataFrame({
    "id": matched_ids,
    "glut": vals[:, 1],
    "gaba": vals[:, 0],
})

agg = df.groupby("id").agg(
    mean_glut=("glut", "mean"),
    mean_gaba=("gaba", "mean"),
)

denom = agg["mean_glut"] + agg["mean_gaba"]
agg["exc_index"] = (agg["mean_glut"] - agg["mean_gaba"]) / denom
agg.loc[denom == 0, "exc_index"] = np.nan

agg["mean_glut"] = agg["mean_glut"].round(2)
agg["mean_gaba"] = agg["mean_gaba"].round(2)
agg["exc_index"] = agg["exc_index"].round(2)

threshold = 0.4
result_df = agg.reset_index()
glut_mask = result_df["exc_index"] > threshold
gaba_mask = result_df["exc_index"] < -threshold
na_mask = ~glut_mask & ~gaba_mask

result_df.loc[glut_mask, "nt_automatic"] = "Glut"
result_df.loc[gaba_mask, "nt_automatic"] = "GABA"
result_df.loc[na_mask, "nt_automatic"] = "na"

df_neurons = (
    df_read.merge(
        result_df,
        on="id",
        how="left"
    )
    .copy()
)

df_ordered = df_neurons[["fish1_ID", "id", "contralateral", "exc_index" , "nt_automatic"]]
df_ordered.to_csv(PATHS.in_neurons("pretectal_fish1.csv"), index=False)
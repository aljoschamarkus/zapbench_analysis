import tensorstore as ts
import numpy as np
import pandas as pd
from config import *

df_read = pd.read_csv(PATHS.in_neurons("pretectal_fish1_pre.csv"))

ds_confocal = ts.open({
    'open': True,
    'driver': GS["fish1_nt"][0],
    'kvstore': GS["fish1_nt"][1]
}).result()

ds_somas = ts.open({
    'open': True,
    'driver': GS["fish1_nt"][0],
    'kvstore': GS["fish1_nt"][1]
}).result()

print(ds_confocal.schema)
print(ds_somas.schema)

conversion_factor_xy = 8/512

x_min_em = 37008
x_max_em = 56054

y_min_em = 30810
y_max_em = 40519

z_min_em = 2908
z_max_em = 5375

x_min = round(x_min_em * conversion_factor_xy)
x_max = round(x_max_em * conversion_factor_xy)

y_min = round(y_min_em * conversion_factor_xy)
y_max = round(y_max_em * conversion_factor_xy)

z_min = z_min_em
z_max = z_max_em

region = ds_somas[x_min:x_max, y_min:y_max, z_min:z_max, 0].read().result()

soma_ids = np.array(df_read["id"].tolist())

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
    # median_ch0=("ch0", "median"),
    # median_ch1=("ch1", "median"),
)
denom = agg["mean_glut"] + agg["mean_gaba"]
agg["exc_index"] = (agg["mean_glut"] - agg["mean_gaba"]) / denom
agg.loc[denom == 0, "exc_index"] = np.nan

agg["mean_glut"] = agg["mean_glut"].round(2)
agg["mean_gaba"] = agg["mean_gaba"].round(2)
agg["exc_index"] = agg["exc_index"].round(2)

# agg["median_ch0"] = agg["median_ch0"].round().astype("Int64")
# agg["median_ch1"] = agg["median_ch1"].round().astype("Int64")

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
df_ordered = df_neurons[["fish1_id", "id", "contralateral", "mean_glut", "mean_gaba", "exc_index" , "nt_manual", "nt_cave", "nt_automatic"]]
df_ordered.to_csv(PATHS.in_neurons("pretectal_fish1.csv"), index=False)

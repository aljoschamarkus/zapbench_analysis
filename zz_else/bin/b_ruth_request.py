import neuprint as neu
import h5py as h5
from private import AUTH_TOKEN
from utils import *
from fishfuncem.em.NeuprintServer import NeuprintServer
import pandas as pd
import os

path = "/Users/aljoscha/Downloads/20260401_RGC-rThDS_3hops - Copy of Inputs-table1.csv"
ruths_list = pd.read_csv(path)
print(ruths_list.columns)

em_ids = ruths_list["bodyId"].tolist()


os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')
nps = NeuprintServer()

cypher_query = f"""
        MATCH (n:Neuron)
        WHERE n.bodyId IN {em_ids}
        RETURN n.bodyId AS bodyId,
        n.zapbenchId AS zap_id
        """

df_ids = neu.fetch_custom(cypher_query)

df_neurons = (
    ruths_list.merge(
        df_ids,
        on="bodyId",
        how="left"
    )
    .copy()
)

ds_data = h5.File(ZAP_DS_H5, "r")
ds_vectors = ds_data["vectors"][:]   # shape: (N, 2)

def safe_vector_lookup(zap_id, ds_vectors):
    if pd.isna(zap_id):
        return None, None
    zap_id = int(zap_id)
    if zap_id < 1 or zap_id > len(ds_vectors):
        return None, None
    return ds_vectors[zap_id - 1][0], ds_vectors[zap_id - 1][1]

vecs = [safe_vector_lookup(zap, ds_vectors) for zap in df_neurons["zap_id"]]
df_neurons["x_vec"] = [v[0] for v in vecs]
df_neurons["y_vec"] = [v[1] for v in vecs]

def safe_color(x, y):
    if pd.isna(x) or pd.isna(y):
        return "#808080"
    return hex_color(x, y)

# sector_info = [hex_color(x, y) for x, y in zip(df_neurons["x_vec"], df_neurons["y_vec"])]
# df_neurons["color"] = [x for x in sector_info]

df_neurons["color"] = [
    safe_color(x, y) for x, y in zip(df_neurons["x_vec"], df_neurons["y_vec"])
]

df_neurons["area"] = "whatever"

for i in df_neurons["group"].unique():
    df_subset = df_neurons.loc[df_neurons["group"] == i]
    # janelia_neuroglancer(df_subset)
    df_neurons.loc[df_neurons["group"] == i, "link"] = janelia_neuroglancer(df_subset)

df_neurons.to_csv('/Users/aljoscha/Downloads/outputs.csv')
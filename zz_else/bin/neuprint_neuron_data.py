import neuprint as neu
import h5py as h5
from private import AUTH_TOKEN
from config import *
from utils import *
from fishfuncem.em.NeuprintServer import NeuprintServer
import pandas as pd

NEURONS_DS_EM_ID = {"thalamus": [7638]}
neuron_ids = NEURONS_DS_EM_ID

ds_data = h5.File(ZAP_DS_H5, "r")
ds_vectors = ds_data["vectors"]

os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')
nps = NeuprintServer()

records = []

for area, ids in neuron_ids.items():
    for id in ids:
        if neuron_ids == NEURONS_DS_ZAP_ID:
            cypher_query = f"""
                MATCH (n:Neuron {{zapbenchId: {id}}})
                RETURN n.zapbenchId AS zap_id,
                       n.bodyId AS bodyId
            """
        elif neuron_ids == NEURONS_DS_EM_ID:
            cypher_query = f"""
                MATCH (n:Neuron {{bodyId: {id}}})
                RETURN n.zapbenchId AS zap_id,
                       n.bodyId AS bodyId
            """
        else:
            raise ValueError
        results_df = neu.fetch_custom(cypher_query)

        if len(results_df) == 0:
            records.append({
                "area": area,
                "zap_id": None,
                "bodyId": int(id) if neuron_ids == NEURONS_DS_EM_ID else None,
            })
            continue

        zap_id_val = results_df["zap_id"].iloc[0]
        body_id_val = results_df["bodyId"].iloc[0]

        records.append({
            "area": area,
            "zap_id": int(zap_id_val) if pd.notna(zap_id_val) else None,
            "bodyId": int(body_id_val) if pd.notna(body_id_val) else None,
        })

df_ids = pd.DataFrame(records)
print(df_ids)

df_neurons_info = nps.get_custom_neuron_list(df_ids["bodyId"].tolist())

df_neurons = (
    df_ids.merge(
        df_neurons_info[["bodyId", "side", "somaLocation"]],
        on="bodyId",
        how="left"
    )
    .copy()
)

print(df_neurons["zap_id"].unique())

# df_neurons["x_vec"] = [ds_vectors[zap - 1][0] for zap in df_neurons["zap_id"]]
# df_neurons["y_vec"] = [ds_vectors[zap - 1][1] for zap in df_neurons["zap_id"]]

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
print(df_neurons)

# df_neurons.to_csv(NEUPRINT_NEURONS_CSV)

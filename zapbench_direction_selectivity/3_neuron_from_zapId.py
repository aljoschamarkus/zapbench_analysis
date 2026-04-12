import neuprint as neu
import h5py as h5
from private import AUTH_TOKEN
from config import *
from utils import *
from fishfuncem.em.NeuprintServer import NeuprintServer
import pandas as pd

ds_data = h5.File(ZAP_DS_H5, "r")
ds_vectors = ds_data["vectors"]
ds_rgb = ds_data["rgb"]

ZAP_IDs = []

os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')
nps = NeuprintServer()

records = []

for area, ids in NEURONS_DS_ZAP_ID.items():
    for zap_id in ids:
        cypher_query = f"""
            MATCH (n:Neuron {{zapbenchId: {zap_id}}})
            RETURN n.zapbenchId AS zapbenchId,
                   n.bodyId AS bodyId
        """
        results_df = neu.fetch_custom(cypher_query)

        if len(results_df) == 0:
            continue

        records.append({
            "area": area,
            "zapbenchId": int(results_df["zapbenchId"].iloc[0]),
            "bodyId": int(results_df["bodyId"].iloc[0]),
        })

df_ids = pd.DataFrame(records)

df_neurons_info = nps.get_custom_neuron_list(df_ids["bodyId"].tolist())

df_neurons = (
    df_ids.merge(
        df_neurons_info[["bodyId", "side", "somaLocation"]],
        on="bodyId",
        how="left"
    )
    .copy()
)

df_neurons["DsXVec"] = [ds_vectors[zap - 1][0] for zap in df_neurons["zapbenchId"]]
df_neurons["DsYVec"] = [ds_vectors[zap - 1][1] for zap in df_neurons["zapbenchId"]]
df_neurons["DsRGB"] = [ds_rgb[zap - 1] for zap in df_neurons["zapbenchId"]]

sector_info = [
    vector_sector(x, y)
    for x, y in zip(df_neurons["DsXVec"], df_neurons["DsYVec"])
]
df_neurons["DsSector"] = [x[0] for x in sector_info]
df_neurons["DsColor"] = [x[1] for x in sector_info]

df_neurons.to_csv(NEUPRINT_NEURONS_CSV)
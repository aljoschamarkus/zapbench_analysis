import neuprint as neu
import h5py as h5
from private import AUTH_TOKEN
from config import *
from utils import *
from fishfuncem.em.NeuprintServer import NeuprintServer
import pandas as pd
from janelia_neuroglancer import janelia_neuroglancer

id = 7638

ds_data = h5.File(ZAP_DS_H5, "r")
ds_vectors = ds_data["vectors"]

os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')
nps = NeuprintServer()

# cypher_query = f"""
#                 MATCH (n:Neuron {{bodyId: {id}}})
#                 RETURN n.zapbenchId AS zap_id,
#                        n.bodyId AS bodyId
#             """

cypher_query = f"""
                MATCH (n:Neuron {{zapbenchId: {id}}})
                RETURN n.zapbenchId AS zap_id,
                       n.bodyId AS bodyId
            """

results_df = neu.fetch_custom(cypher_query)
print(results_df)

df_neurons_info = nps.get_custom_neuron_list(results_df["bodyId"].tolist())

df_neurons = (
    results_df.merge(
        df_neurons_info[["bodyId", "side"]],
        on="bodyId",
        how="left"
    )
    .copy()
)
print(df_neurons)

ds_data = h5.File(ZAP_DS_H5, "r")
ds_vectors = ds_data["vectors"]

df_neurons["x_vec"] = [ds_vectors[zap - 1][0] for zap in df_neurons["zap_id"]]
df_neurons["y_vec"] = [ds_vectors[zap - 1][1] for zap in df_neurons["zap_id"]]

sector_info = [hex_color(x, y) for x, y in zip(df_neurons["x_vec"], df_neurons["y_vec"])]
df_neurons["color"] = [x for x in sector_info]

df_neurons["area"] = "thalamus"

janelia_neuroglancer(df_neurons)
import neuprint as neu
from config import *
from private import AUTH_TOKEN
import os
import pandas as pd
from utils import ids_to_df_neurons
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

all_pretectal_zap = pd.read_csv(PATHS.in_data("neurons_pretectum.csv"))

os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')

connectivity_raw = neu.fetch_simple_connections(
    upstream_criteria=all_pretectal_zap,
    downstream_criteria=THALAMIC_EM_IDS,
    min_weight=1,
    client=c,
)

connectivity = connectivity_raw.drop(columns=['type_pre', 'type_post', 'instance_pre', 'instance_post', "conn_roiInfo"])

pre_df = ids_to_df_neurons(connectivity["bodyId_pre"].tolist(), id_type="em")
post_df = ids_to_df_neurons(connectivity["bodyId_post"].tolist(), id_type="em")

df_merge1 = (
    connectivity.merge(
        pre_df,
        left_on="bodyId_pre",
        right_on="bodyId",
        how="left"
    )
    .copy()
)

df_merge2 = df_merge1.merge(
    post_df,
    left_on="bodyId_post",
    right_on="bodyId",
    how="left",
    suffixes=("_1", "_2")
)

df_neurons =df_merge2.dropna(axis="rows")

mask_ipsi = df_neurons["side_1"] == df_neurons["side_2"]
mask_contra = df_neurons["side_1"] != df_neurons["side_2"]

df_neurons.loc[mask_ipsi, "connection"] = "ipsi"
df_neurons.loc[mask_contra, "connection"] = "contra"

v1x = df_neurons["x_scaled_1"]
v1y = df_neurons["y_scaled_1"]

v2x = df_neurons["x_scaled_2"]
v2y = df_neurons["y_scaled_2"]

dot = v1x * v2x + v1y * v2y

norm1 = np.sqrt(v1x**2 + v1y**2)
norm2 = np.sqrt(v2x**2 + v2y**2)

df_neurons["cosine_similarity"] = dot / (norm1 * norm2)

df_neurons.to_csv("/Users/aljoscha/Downloads/whatev.csv", index=False)

mask = (norm1 > 0.03099864721298218) & (norm2 > 0.03099864721298218)

df_neurons_thresholded = df_neurons.loc[mask]

df_neurons.loc[df_neurons["connection"] == "ipsi", "connection"] = "ipsilateral"
df_neurons.loc[df_neurons["connection"] == "contra", "connection"] = "contralateral"
df_neurons.rename(columns={"connection": "connection type", "cosine_similarity": "cosine similarity"}, inplace=True)

df_neurons_thresholded.loc[df_neurons_thresholded["connection"] == "ipsi", "connection"] = "ipsilateral"
df_neurons_thresholded.loc[df_neurons_thresholded["connection"] == "contra", "connection"] = "contralateral"
df_neurons_thresholded.rename(columns={"connection": "connection type", "cosine_similarity": "cosine similarity"}, inplace=True)

plt.style.use('dark_background')

sns.violinplot(x="connection type", y="cosine similarity", data=df_neurons, cut=0, color=(0.1216, 0.4667, 0.7059))
sns.swarmplot(x="connection type", y="cosine similarity", data=df_neurons, alpha=0.5, color=(1.0, 0.4980, 0.0549))
# plt.show()
plt.savefig(PATHS.in_plots("cos_sim.png"))
plt.close()

sns.violinplot(x="connection type", y="cosine similarity", data=df_neurons_thresholded, cut=0, color=(0.1216, 0.4667, 0.7059))
sns.swarmplot(x="connection type", y="cosine similarity", data=df_neurons_thresholded, alpha=0.5, color=(1.0, 0.4980, 0.0549))
# plt.show()
plt.savefig(PATHS.in_plots("cos_sim_threshold.png"))
plt.close()
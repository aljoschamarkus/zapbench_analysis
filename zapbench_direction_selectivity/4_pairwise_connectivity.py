import neuprint as neu
import numpy as np
from private import AUTH_TOKEN
from config import *
import pandas as pd
from tqdm import tqdm

os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')

neurons_df = pd.read_csv(NEUPRINT_NEURONS_CSV)
pretectal_mask = neurons_df["area"] == "Pretectum"
thalamic_mask = neurons_df["area"] == "Thalamus"

pre_IDs = neurons_df.loc[pretectal_mask, "bodyId"].values
post_IDs = neurons_df.loc[thalamic_mask, "bodyId"].values

print(len(pre_IDs))
print(pre_IDs)
print(len(post_IDs))
print(post_IDs)

for pre_ID in tqdm(pre_IDs):
    for post_ID in post_IDs:

        path = neu.fetch_paths(pre_ID, post_ID, min_weight=0,
                                timeout=5.0,
                                # path_length=0,
                               max_path_length=1,
                                client=None)

        if len(path) > 0:
            length = path['path_length'][0]
            pre = list(path["bodyId"])[0]
            post = list(path["bodyId"])[-1]
            zap_pre = neurons_df.loc[neurons_df["bodyId"] == pre, "zapbenchId"].iloc[0]
            zap_post = neurons_df.loc[neurons_df["bodyId"] == post, "zapbenchId"].iloc[0]
            vec_pre = neurons_df.loc[neurons_df["bodyId"] == pre, ["DsXVec", "DsYVec"]].iloc[0].to_numpy()
            vec_post = neurons_df.loc[neurons_df["bodyId"] == post, ["DsXVec", "DsYVec"]].iloc[0].to_numpy()
            cos_sim = np.dot(vec_pre, vec_post) / (np.linalg.norm(vec_pre) * np.linalg.norm(vec_post))
            print(f"ZAP_ID: {zap_pre}-{zap_post}\nEM_ID: {pre}-{post}\npath_length={length}\ncos_sim={cos_sim}")

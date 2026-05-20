import pandas as pd
import numpy as np
from config import *

vector_left = [0, -1]
# vector_left = [1, 0]
vector_right = [0, 1]
# vector_right = [-1, 0]

neurons_df = pd.read_csv(NEUPRINT_NEURONS_CSV)
# print(neurons_df.head())

mask_thalamus = neurons_df["area"] == "Thalamus"
mask_pretectum = neurons_df["area"] == "Pretectum"
mask_left = neurons_df["side"] == "left"
mask_right = neurons_df["side"] == "right"

vectors_left = neurons_df.loc[mask_left, ["DsXVec", "DsYVec"]].to_numpy()
print(len(vectors_left))
vectors_right = neurons_df.loc[mask_right, ["DsXVec", "DsYVec"]].to_numpy()
print(len(vectors_right))
vectors_all = neurons_df[["DsXVec", "DsYVec"]].to_numpy()

print(vectors_left.shape)

# cos_sim = np.dot(vec_pre, vec_post) / (np.linalg.norm(vec_pre) * np.linalg.norm(vec_post))

def cosine_similarity_to_reference(vectors, reference, eps=1e-12):
    ref_norm = np.linalg.norm(reference)
    vec_norms = np.linalg.norm(vectors, axis=1)

    valid = vec_norms > eps
    sims = np.full(len(vectors), np.nan)

    sims[valid] = (vectors[valid] @ reference) / (vec_norms[valid] * ref_norm)
    return sims

cos_all_l = cosine_similarity_to_reference(vectors_all, vector_left)
cos_all_r = cosine_similarity_to_reference(vectors_all, vector_right)
cos_left = cosine_similarity_to_reference(vectors_left, vector_left)
cos_left_r = cosine_similarity_to_reference(vectors_left, vector_right)
cos_right = cosine_similarity_to_reference(vectors_right, vector_right)
cos_right_l = cosine_similarity_to_reference(vectors_right, vector_left)

print("All mean cosine similarity:", np.nanmean(cos_all_l), np.nanmean(cos_all_r))
print("Left mean cosine similarity:", np.nanmean(cos_left), np.nanmean(cos_left_r))
print("Right mean cosine similarity:", np.nanmean(cos_right), np.nanmean(cos_right_l))

print("All median cosine similarity:", np.nanmedian(cos_all_l), np.nanmedian(cos_all_r))
print("Left median cosine similarity:", np.nanmedian(cos_left), np.nanmedian(cos_left_r))
print("Right median cosine similarity:", np.nanmedian(cos_right), np.nanmedian(cos_right_l))

import matplotlib.pyplot as plt

plt.figure(figsize=(6, 6))
plt.quiver(
    np.zeros(len(vectors_left)), np.zeros(len(vectors_left)),
    vectors_left[:, 0], vectors_left[:, 1],
    angles='xy', scale_units='xy', scale=1
)
plt.axis('equal')
plt.xlim(-1, 1)
plt.ylim(-1, 1)
plt.title("Left vectors")
plt.show()

plt.figure(figsize=(6, 6))
plt.quiver(
    np.zeros(len(vectors_right)), np.zeros(len(vectors_right)),
    vectors_right[:, 0], vectors_right[:, 1],
    angles='xy', scale_units='xy', scale=1
)
plt.axis('equal')
plt.xlim(-1, 1)
plt.ylim(-1, 1)
plt.title("Right vectors")
plt.show()
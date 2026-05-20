import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from config import PATHS

path = "/Users/aljoscha/Downloads/zapbench_data_thalamus/ds_thalamic_neurons - pretectal_fish1.csv"
df = pd.read_csv(path)

mask_contra = df["contralateral"]
mask_GABA = df["neurotransmitter"] == "GABA"
mask_Glut = df["neurotransmitter"] == "Glut"
mask_neither = ~mask_GABA & ~mask_Glut

df_contra = df.loc[mask_contra]
df_ispsi = df.loc[~mask_contra]

species = (
    "all",
    "ipsi",
    "contra",
)

weight_counts = {
    "VGluT2": np.array([len(df.loc[mask_Glut])/len(df), len(df_ispsi[mask_Glut])/len(df_ispsi), len(df_contra.loc[mask_Glut])/len(df_contra)]),
    "Gad1B": np.array([len(df.loc[mask_GABA])/len(df), len(df_ispsi[mask_GABA])/len(df_ispsi), len(df_contra[mask_GABA])/len(df_contra)]),
    "unknown": np.array([len(df.loc[mask_neither])/len(df), len(df_ispsi[mask_neither])/len(df_ispsi), len(df_contra[mask_neither])/len(df_contra)]),
}

colors = {
    "VGluT2": (0, 1, 0),
    "Gad1B": (1, 0, 1),
    "unknown": (217/255, 217/255, 217/255),
}
width = 0.5

plt.style.use('dark_background')

fig, ax = plt.subplots(1, 2, sharey=True, width_ratios=[0.2, 1])
fig.subplots_adjust(wspace=1.5)
bottom = np.zeros(3)

for boolean, weight_count in weight_counts.items():
    p = ax[1].bar(species, weight_count, width, label=boolean, bottom=bottom, color=colors[boolean])
    bottom += weight_count

p2 = ax[0].bar("all", len(df_ispsi)/len(df), width, label="ipsi", bottom=0, color=(31/255, 119/255, 180/255))
p3 = ax[0].bar("all", len(df_contra)/len(df), width, label="contra", bottom=len(df_contra)/len(df), color=(255/255, 127/255, 14/255))

# fig.suptitle('Potentially direction selective pretectal neurons (N=47)', fontsize=16)
# ax[1].legend(loc="upper right")
ax[1].legend(loc="upper left", bbox_to_anchor=(-0.9, 0.4), fontsize=16)
ax[1].set_title("neurotransmitter identity", fontsize=16)
ax[1].tick_params(labelsize=16)
ax[0].tick_params(labelsize=16)
ax[0].spines['top'].set_visible(False)
ax[1].spines['top'].set_visible(False)
ax[0].spines['right'].set_visible(False)
ax[1].spines['right'].set_visible(False)
ax[0].set_ylabel("Share of population", fontsize=16)
ax[0].legend(loc="upper right", bbox_to_anchor=(5, 0.8), fontsize=16)
ax[0].set_title("axonic projection", fontsize=16)
# plt.show()
plt.savefig(PATHS.in_plots("bar_chart.png"), format="png", dpi=1000)
plt.close()

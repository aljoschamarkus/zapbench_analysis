import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
    "contralateral",
    "ipsilateral",
)

weight_counts = {
    "Glut": np.array([len(df.loc[mask_Glut])/len(df), len(df_contra.loc[mask_Glut])/len(df_contra), len(df_ispsi[mask_Glut])/len(df_ispsi)]),
    "GABA": np.array([len(df.loc[mask_GABA])/len(df), len(df_contra[mask_GABA])/len(df_contra), len(df_ispsi[mask_GABA])/len(df_ispsi)]),
    "NA": np.array([len(df.loc[mask_neither])/len(df), len(df_contra[mask_neither])/len(df_contra), len(df_ispsi[mask_neither])/len(df_ispsi)]),
}

colors = {
    "Glut": "lime",
    "GABA": "magenta",
    "NA": "grey"
}
width = 0.5

fig, ax = plt.subplots(1, 2, sharey=True, width_ratios=[0.2, 1])
bottom = np.zeros(3)

for boolean, weight_count in weight_counts.items():
    p = ax[1].bar(species, weight_count, width, label=boolean, bottom=bottom, color=colors[boolean])
    bottom += weight_count

p2 = ax[0].bar("all", len(df_contra)/len(df), width, label="contra", bottom=0, color="C1")
p3 = ax[0].bar("all", len(df_ispsi)/len(df), width, label="ipsi", bottom=len(df_contra)/len(df), color="C0")



fig.suptitle('Direction selective thalamic neuron features (fish1, N=47)')
fig.supxlabel('Google sheet:\nhttps://docs.google.com/spreadsheets/d/13QOqf9SwgmFEzKOpOkgT1OJyPlZ-wxlZ5IZdEuoR2ag/edit?gid=1140184864#gid=1140184864', fontsize=6
              )
ax[1].legend(loc="upper right")
ax[1].set_title("neurotransmitter identity")
ax[0].set_ylabel("ratio of (sub-) population")
ax[0].legend(loc="upper left")
ax[0].set_title("axonic projection")
plt.show()
# plt.savefig("/Users/aljoscha/Downloads/nt_identity.pdf", format="pdf")
# plt.close()

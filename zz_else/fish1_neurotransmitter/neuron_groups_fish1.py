import pandas as pd

path = "/Users/aljoscha/Downloads/zapbench_data_thalamus/ds_thalamic_neurons - pretectal_fish1.csv"
df = pd.read_csv(path)

mask_contra = df["contralateral"]
mask_GABA = df["neurotransmitter"] == "GABA"
mask_Glut = df["neurotransmitter"] == "Glut"
mask_neither = ~mask_GABA & ~mask_Glut

contra_all = df.loc[mask_contra, "fish1_ID"].values
ipsi_all = df.loc[~mask_contra, "fish1_ID"].values

contra_GABA = df.loc[mask_contra & mask_GABA, "fish1_ID"].values
contra_Glut = df.loc[mask_contra & mask_Glut, "fish1_ID"].values
contra_neither = df.loc[mask_contra & mask_neither, "fish1_ID"].values

ipsi_GABA = df.loc[~mask_contra & mask_GABA, "fish1_ID"].values
ipsi_Glut = df.loc[~mask_contra & mask_Glut, "fish1_ID"].values
ipsi_neither = df.loc[~mask_contra & mask_neither, "fish1_ID"].values

print("contra_all", contra_all)
print("ipsi_all", ipsi_all)
print("contra_GABA", contra_GABA)
print("contra_Glut", contra_Glut)
print("contra_neither", contra_neither)
print("ipsi_GABA", ipsi_GABA)
print("ipsi_Glut", ipsi_Glut)
print("ipsi_neither", ipsi_neither)
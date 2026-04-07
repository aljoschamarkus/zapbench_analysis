import pandas as pd

path = "/Users/aljoscha/Downloads/ds_thalamic_neurons - pretectal_fish1.csv"
df = pd.read_csv(path)

mask_contra = df["contralateral"]
mask_GABA = df["neurotransmitter"] == "GABA"
mask_Glut = df["neurotransmitter"] == "Glut"

list_magenta = df.loc[mask_contra & mask_GABA, "fish1_ID"]
list_green = df.loc[mask_contra & mask_Glut, "fish1_ID"]
list_ipsi = df.loc[~mask_contra, "fish1_ID"]
list_contra_na = df.loc[mask_contra & ~mask_GABA & ~mask_Glut, "fish1_ID"]

list = [list_magenta, list_green, list_ipsi, list_contra_na]

for sub in list:
    print(len(sub))
    for val in sub:
        print(val)

# print(list_magenta.values)
# print(list_green.values)
# print(list_ipsi.values)
# print(list_contra_na.values)
#
print(len(list_magenta) + len(list_green) + len(list_ipsi) + len(list_contra_na))
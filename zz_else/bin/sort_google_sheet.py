import pandas as pd

df_pretec_raw = pd.read_csv('/Users/aljoscha/Downloads/ds_thalamic_neurons - pretectal_fish1.csv')

df_pretec = df_pretec_raw[["fish1_ID", "contralateral", "neurotransmitter"]]
df_pretec.rename(columns={"fish1_ID": "fish1_id", "neurotransmitter": "nt_manual"}, inplace=True)

df_somas_raw = pd.read_csv('/Users/aljoscha/Downloads/somas.csv', delimiter='\t')
df_somas = df_somas_raw[["pt_root_id", "id", "cell_type"]]
df_somas.loc[df_somas["cell_type"] == "exc", "cell_type"] = "Glut"
df_somas.loc[df_somas["cell_type"] == "inh", "cell_type"] = "GABA"
df_somas.rename(columns={"pt_root_id": "fish1_id", "cell_type": "nt_cave"}, inplace=True)

df_neurons = (
    df_pretec.merge(
        df_somas,
        on="fish1_id",
        how="left"
    )
    .copy()
)
df_neurons.to_csv('/Users/aljoscha/Downloads/neurons2.csv', index=False)
print(df_neurons)


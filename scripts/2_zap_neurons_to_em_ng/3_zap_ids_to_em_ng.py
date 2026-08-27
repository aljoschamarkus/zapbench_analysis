from utils import *
from config import *
import pandas as pd
import requests
from io import StringIO

# Initial selection based on direction selectivity
r = requests.get(url_fish2_thalamic)
r.raise_for_status()

df = pd.read_csv(StringIO(r.text))
df_neurons = ids_to_df_neurons(df["ZAPB_ID"].tolist(), id_type="zap")

# Refined selection based on morphology
# df_neurons = ids_to_df_neurons(THALAMIC_EM_IDS, id_type="em")

print(janelia_neuroglancer(df_neurons))
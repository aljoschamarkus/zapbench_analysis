from utils import *
from config import *

# df_neurons = ids_to_df_neurons(df["bodyId"].tolist(), id_type="em")

# ZAP_IDs = [
# 9061, 9075, 9113, 9118, 9131, 9136, 9140, 9142, 9160, 9162, 9172, 9225, 9256, 21545, 21573, 21603, 21608, 21623, 21669, 21676, 21698, 21713, 21722, 21731, 21732
# ]

# df_neurons = ids_to_df_neurons(ZAP_IDs)
# df_neurons = ids_to_df_neurons(THALAMIC_DS_ZAP_ID, id_type="zap")

EM_IDs = [100459637, 100489572, 100554843, 100606891, 100872084, 100960836, 101375512, 101655767, 101905119, 102763559, 104512644, 105340332, 106132947, 106196373, 109686908]

df_neurons = ids_to_df_neurons(EM_IDs, id_type="em")

print(janelia_neuroglancer(df_neurons))
import tensorstore as ts
import numpy as np
import h5py as h5
from config import *

mece_2_ds = ts.open({
    'open': True,
    'driver': GS["zap_mece_pretectum"][0],
    'kvstore': GS["zap_mece_pretectum"][1],
}).result()

print(mece_2_ds.schema)

mece_2 = mece_2_ds[:, :, :, 0].read().result()
mask_pretectum = mece_2 == 14
pretectum = np.where(mask_pretectum)

with h5.File(PATHS.in_data("zap_mece_pretectum.h5") , "w") as f:
    f.create_dataset("mask_pretectum", data=mask_pretectum, compression="gzip")
    f.create_dataset("pretectum", data=pretectum, compression="gzip")
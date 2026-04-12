import h5py as h5
from config import ZAP_DS_H5

ds_data = h5.File(ZAP_DS_H5, "r")
ds_rgb = ds_data["rgb"]

#

IDs = [
22400,
22179,
32767,
22145,
22145,
24239,
22361,
22361,
22343,
22343,
22353,
22342,
9739
]

for id in IDs:
    print(f"ZAPBench ID: {id} | RGB: {ds_rgb[id-1]}")
    print(f"{int(ds_rgb[id-1][0])}, {int(ds_rgb[id-1][1])}, {int(ds_rgb[id-1][2])}")
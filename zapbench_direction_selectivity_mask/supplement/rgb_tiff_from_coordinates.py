import tifffile

path = "/Users/aljoscha/Downloads/colormapbigfull.tif"
img = tifffile.imread(path) # shape: (z, y, x, c)
print(img.shape)

"""
Tiff shape: (z, y, x, c)
Data transfrom to match zapbench space:
    Flip x_tiff: img_flipped = np.flip(img, axis=2)
    Transform matrix:
        0, 1, 0, 0, 0       x_zap       -> y_tiff (flipped)
        0, 0, 1, 0, 0       y_zap       -> x_tiff
        1, 0, 0, 0, -1      z_zap (+1)  -> z_tiff 
        0, 0, 0, 1, 0
"""

# copy neuroglancer x, y, z voxel coordinates here
x_zap, y_zap, z_zap = 1037, 736, 35

# untransformed tiff (z, y, x)
# z_tiff_c, y_tiff_c, x_tiff_c = 36, 1037, 591
# print(f"{z_tiff_c}, {y_tiff_c}, {x_tiff_c} test")

z_tiff = z_zap + 1
y_tiff = x_zap
x_tiff = img.shape[2] - 1 - y_zap
print(f"Voxel coordinates (z, y, x): {z_tiff}, {y_tiff}, {x_tiff}")

rgb = img[z_tiff, y_tiff, x_tiff, :]
print(f"RGB value:{rgb[0]}, {rgb[1]}, {rgb[2]}")
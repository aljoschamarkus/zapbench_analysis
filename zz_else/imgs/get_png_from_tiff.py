import tifffile
from PIL import Image
import numpy as np

path = "/Users/aljoscha/Downloads/tiff_stack.tif"
file = tifffile.imread(path)

slice_img = file[24, 700:1200, 450:850]
print(slice_img.shape)
img_transposed = np.transpose(slice_img, (1, 0, 2))
img = Image.fromarray(img_transposed.astype("uint8"))

img.save("/Users/aljoscha/Downloads/slice_10.png", dpi=(1000, 1000))
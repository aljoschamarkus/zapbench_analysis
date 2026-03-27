import numpy as np
from utils import vector_to_rgb

H, W = 200, 200
x = np.linspace(-1, 1, W)
y = np.linspace(-1, 1, H)
X, Y = np.meshgrid(x, y)

rgb = vector_to_rgb(X, Y)

import matplotlib.pyplot as plt
plt.imshow(rgb, origin="lower")
plt.show()
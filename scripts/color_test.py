import numpy as np
from matplotlib.colors import hsv_to_rgb

def vector_to_rgb(vx, vy):
    """
    vx, vy: arrays of same shape
    returns: rgb array of shape vx.shape + (3,)
    """

    # angle in [-pi, pi] -> hue in [0, 1)
    hue = (np.arctan2(vy, vx) / (2 * np.pi)) % 1.0

    # brightness from L-infinity norm, clipped to [0, 1]
    val = np.maximum(np.abs(vx), np.abs(vy))
    val = np.clip(val, 0, 1)

    # full saturation everywhere except origin stays black because val=0
    sat = np.ones_like(val)

    hsv = np.stack([hue, sat, val], axis=-1)
    rgb = hsv_to_rgb(hsv)
    return rgb


H, W = 200, 200
x = np.linspace(-1, 1, W)
y = np.linspace(-1, 1, H)
X, Y = np.meshgrid(x, y)

rgb = vector_to_rgb(X, Y)

import matplotlib.pyplot as plt
plt.imshow(rgb, origin="lower")
plt.show()
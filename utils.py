import numpy as np

def map_circ_to_square(x, y):
    square = np.maximum(np.abs(x), np.abs(y))
    return square

def vector_to_rgb(vx, vy, threshold=97):
    from matplotlib.colors import hsv_to_rgb
    # mag = np.maximum(np.abs(vx), np.abs(vy))
    mag = map_circ_to_square(vx, vy)
    scale = np.percentile(mag, threshold)
    vx, vy = vx / (scale + 1e-6), vy / (scale + 1e-6)
    hue = (1.0 - ((np.arctan2(vy, vx) / (2 * np.pi) - 2 / 6) % 1.0)) % 1.0
    # val = np.maximum(np.abs(vx), np.abs(vy))
    val = map_circ_to_square(vx, vy)
    val = np.clip(val, 0, 1)
    sat = np.ones_like(val)
    hsv = np.stack([hue, sat, val], axis=-1)
    rgb = hsv_to_rgb(hsv)
    return rgb
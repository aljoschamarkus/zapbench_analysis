def vector_to_rgb(vx, vy, threshold=98):
    import numpy as np
    from matplotlib.colors import hsv_to_rgb
    mag = np.maximum(np.abs(vx), np.abs(vy))
    scale = np.percentile(mag, threshold)
    vx, vy = vx / (scale + 1e-6), vy / (scale + 1e-6)
    hue = (1.0 - ((np.arctan2(vy, vx) / (2 * np.pi) - 2 / 6) % 1.0)) % 1.0
    val = np.maximum(np.abs(vx), np.abs(vy))
    val = np.clip(val, 0, 1)
    sat = np.ones_like(val)
    hsv = np.stack([hue, sat, val], axis=-1)
    rgb = hsv_to_rgb(hsv)
    return rgb

def data_shape(var1, var2, var3, var4):
    from tensorstore import open
    data = open({
        'open': True,
        'driver': 'zarr3',
        'kvstore': 'gs://zapbench-release/volumes/20240930/aligned'
    }).result()
    shape_d = data.shape
    x, y, z, t = shape_d[0], shape_d[1], shape_d[2], shape_d[3]
    order = {
        "x": x,
        "y": y,
        "z": z,
        "t": t,
    }
    output = (order[var1], order[var2], order[var3], order[var4])
    return output
def stimulus_indices(path):
    import h5py as h5
    f_stim = h5.File(path, "r")

    condition_t_full = f_stim["condition_t"][:]
    start_index = condition_t_full.min()
    # condition_t = condition_t_full - start_index

    stim_off_t = f_stim["stim_off_t"][:] - start_index
    forward_t = f_stim["forward_t"][:] - start_index
    right_t = f_stim["right_t"][:] - start_index
    backward_t = f_stim["backward_t"][:] - start_index
    left_t = f_stim["left_t"][:] - start_index

    list_conditions = [forward_t, right_t, backward_t, left_t]
    return stim_off_t, list_conditions

def ds_vectors(path, t_axis, condition_t, list_conditions):
    from tqdm import tqdm
    import h5py as h5
    import numpy as np

    f_data = h5.File(path, "r")
    data = f_data["data"]

    n_t = data.shape[t_axis]
    condition_t_valid = condition_t[(condition_t >= 0) & (condition_t < n_t)]

    if t_axis == 0:
        data_off = data[condition_t_valid, :]
        print(data_off.shape)
    else:
        data_off = data[:, :, :, condition_t_valid]
    background_off = data_off.mean(axis=t_axis)

    stimuli = []
    for cond_t in tqdm(list_conditions):
        cond_t = cond_t[(cond_t >= 0) & (cond_t < n_t)]
        if t_axis == 0:
            data_t = data[cond_t, :]
        else:
            data_t = data[:, :, :, cond_t]
        data_mean = data_t.mean(axis=t_axis)
        img_bs = data_mean - background_off
        stimuli.append(img_bs)

    stimuli_np = np.array(stimuli)

    vector_x = stimuli_np[0] - stimuli_np[2]
    vector_y = stimuli_np[1] - stimuli_np[3]
    return vector_x, vector_y

def vector_to_rgb(vx, vy, threshold=98):
    import numpy as np
    from matplotlib.colors import hsv_to_rgb
    mag = np.maximum(np.abs(vx), np.abs(vy))
    scale = np.percentile(mag, threshold)
    vx, vy = vx / (scale + 1e-6), vy / (scale + 1e-6)
    # hue = (1.0 - ((np.arctan2(vy, vx) / (2 * np.pi) - 2 / 6) % 1.0)) % 1.0
    hue = (np.arctan2(vy, vx) / (2 * np.pi) + 2 / 6) % 1.0
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

def img_to_ng(layers):
    import neuroglancer as ng
    from numpy import min, max
    PORT = 8080
    ng.set_server_bind_address("127.0.0.1", PORT)

    in_dimensions = ng.CoordinateSpace(
        names=["z", "y", "x"],
        scales=[1, 1, 1],
    )

    out_dimensions = ng.CoordinateSpace(
        names=["x", "y", "z"],
        scales=[1, 1, 1],
    )

    matrix = [
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 0, 0, 0],
    ]

    viewer = ng.Viewer()

    with viewer.txn() as s:
        for name, img in layers.items():
            img_scaled = (img-min(img))/(max(img)-min(img))
            s.layers[name] = ng.ImageLayer(
                source=ng.LayerDataSource(
                    url=ng.LocalVolume(
                        data=img_scaled,
                        dimensions=in_dimensions,
                    ),
                    transform=ng.CoordinateSpaceTransform(
                    matrix=matrix,
                    output_dimensions=out_dimensions,
                    )
                )
            )

        s.layout = "xy"

    print(viewer)
    input("stop server...")

def rgb_to_hex(rgb):
    import numpy as np
    rgb = np.clip(np.asarray(rgb), 0, 1)
    return "#{:02x}{:02x}{:02x}".format(
        int(round(rgb[0] * 255)),
        int(round(rgb[1] * 255)),
        int(round(rgb[2] * 255)),
    )

def vector_sector(vx, vy, value=1.0):
    if vx == 0 and vy == 0:
        return None, "Zero", "#000000"
    import numpy as np
    from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
    SECTOR_NAMES = ["Forward", "FR", "Right", "BR", "Back", "BL", "Left", "FL"]

    angle = np.arctan2(vy, vx) % (2 * np.pi)
    sector_idx = int(((angle + np.pi / 8) % (2 * np.pi)) // (np.pi / 4))
    sector_name = SECTOR_NAMES[sector_idx]

    center_angle = sector_idx * (np.pi / 4)

    # same style as your hue mapping, but using sector center
    hue = (center_angle / (2 * np.pi) + 2 / 6) % 1.0

    rgb = hsv_to_rgb([hue, 1.0, value])
    hex_color = rgb_to_hex(rgb)

    # return sector_idx, sector_name, hex_color
    return [sector_idx, hex_color]
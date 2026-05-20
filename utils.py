def stimulus_indices(path):
    import h5py as h5
    f_stim = h5.File(path, "r")

    condition_t_full = f_stim["condition_t"][:]
    start_index = condition_t_full.min()

    stim_off_t = f_stim["stim_off_t"][:] - start_index
    forward_t = f_stim["forward_t"][:] - start_index
    right_t = f_stim["right_t"][:] - start_index
    backward_t = f_stim["backward_t"][:] - start_index
    left_t = f_stim["left_t"][:] - start_index

    list_conditions = [forward_t, right_t, backward_t, left_t]
    return stim_off_t, list_conditions

def ds_vectors(path, t_axis, stim_off_t, list_conditions):
    from tqdm import tqdm
    import h5py as h5
    import numpy as np

    f_data = h5.File(path, "r")
    data = f_data["data"]

    n_t = data.shape[t_axis]
    condition_t_valid = stim_off_t[(stim_off_t >= 0) & (stim_off_t < n_t)]

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

    vector_x = stimuli_np[1] - stimuli_np[3]
    vector_y = stimuli_np[0] - stimuli_np[2]
    return vector_x, vector_y

def vector_to_rgb(vx, vy, threshold=98):
    import numpy as np
    from matplotlib.colors import hsv_to_rgb
    mag = np.maximum(np.abs(vx), np.abs(vy))
    scale = np.percentile(mag, threshold)
    vx, vy = vx / (scale + 1e-6), vy / (scale + 1e-6)
    hue = (np.arctan2(vx, vy) / (2 * np.pi) + 2 / 6) % 1.0
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

def hex_color(vx, vy, value=1.0):
    import numpy as np
    from matplotlib.colors import hsv_to_rgb, to_hex

    if np.isnan(vx) or np.isnan(vy):
        return "#808080"

    if vx == 0 and vy == 0:
        return "#000000"

    angle = np.arctan2(vx, vy) % (2 * np.pi)
    hue = (angle / (2 * np.pi) + 2 / 6) % 1.0

    rgb = hsv_to_rgb([hue, 1.0, value])
    return to_hex(rgb)

def square_to_circ(x, y):
    import numpy as np

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = ~np.isnan(x) & ~np.isnan(y)
    zero = valid & (x == 0) & (y == 0)
    nonzero = valid & ~zero

    u = np.full_like(x, np.nan, dtype=float)
    v = np.full_like(y, np.nan, dtype=float)

    angle = np.full_like(x, np.nan, dtype=float)
    angle[nonzero] = np.arctan2(y[nonzero], x[nonzero])

    r = np.full_like(x, np.nan, dtype=float)
    r[nonzero] = np.maximum(np.abs(x[nonzero]), np.abs(y[nonzero]))
    r[zero] = 0.0

    u[nonzero] = r[nonzero] * np.cos(angle[nonzero])
    v[nonzero] = r[nonzero] * np.sin(angle[nonzero])
    u[zero] = 0.0
    v[zero] = 0.0

    return u, v

def ids_to_df_neurons(ids, id_type="zap"):
    """
    get data frame of ZAPBench Ids, EM Ids and side indication from list of ZAPBench Ids
    parameters: zap_ids (list), ids ["zap", "em"]
    returns: df["EM_IDs", "ZAP_IDs", "side"]
    """
    import os
    from private import AUTH_TOKEN
    import neuprint as neu
    from fishfuncem.em.NeuprintServer import NeuprintServer
    import h5py as h5
    from config import PATHS
    import pandas as pd
    import numpy as np

    os.environ['NEUPRINT_APPLICATION_CREDENTIALS'] = AUTH_TOKEN
    c = neu.Client('neuprint-fish2.janelia.org', dataset='fish2')
    nps = NeuprintServer()

    if id_type == "zap":
        cypher_query = f"""
                MATCH (n:Neuron)
                WHERE n.zapbenchId IN {ids}
                RETURN n.bodyId AS bodyId,
                n.zapbenchId AS zap_id
                """
    elif id_type == "em":
        cypher_query = f"""
                MATCH (n:Neuron)
                WHERE n.bodyId IN {ids}
                RETURN n.bodyId AS bodyId,
                n.zapbenchId AS zap_id
                """
    else:
        raise ValueError("id_type must be 'zap' or 'em'")

    df_ids = neu.fetch_custom(cypher_query)
    df_neurons_info = nps.get_custom_neuron_list(df_ids["bodyId"].tolist())

    df_neurons = (
        df_ids.merge(
            df_neurons_info[["bodyId", "side"]],
            on="bodyId",
            how="left"
        )
        .copy()
    )

    traces_data = h5.File(PATHS.in_data("zap_direction_selectivity.h5"), "r")
    vecs_scaled = traces_data["vectors_scaled"]
    colors = traces_data["hex_color"][:].astype("str")

    # df_neurons["color"] = [colors[zap - 1] for zap in df_neurons["zap_id"]]

    # df_neurons["color"] = [
    #     colors[zap - 1] if zap is not None else "#808080"
    #     for zap in df_neurons["zap_id"]
    # ]

    def zap_to_color(zap):
        if pd.isna(zap):
            return "#808080"

        zap = int(zap)
        if 1 <= zap <= len(colors):
            return colors[zap - 1]

        # return "#808080"

    df_neurons["color"] = [zap_to_color(zap) for zap in df_neurons["zap_id"]]

    # df_neurons["x_scaled"] = [vecs_scaled[zap - 1][0] for zap in df_neurons["zap_id"]]
    # df_neurons["y_scaled"] = [vecs_scaled[zap - 1][1] for zap in df_neurons["zap_id"]]

    def zap_to_vector_scaled(zap):
        if pd.isna(zap):
            return [np.nan, np.nan]

        zap = int(zap)
        if 1 <= zap <= len(vecs_scaled):
            return vecs_scaled[zap - 1]

        # return [np.nan, np.nan]

    df_neurons["x_scaled"], df_neurons["y_scaled"] = zip(
        *[zap_to_vector_scaled(zap) for zap in df_neurons["zap_id"]]
    )
    return df_neurons

def janelia_neuroglancer(df):
    import json
    import urllib.parse
    import requests
    seg_source = [
        {
            "url": "dvid://https://fishemf-cleaving.janelia.org/c9df3e/segmentation?dvid-service=https://ngsupport-bmcp5imp6q-uk.a.run.app",
            "subsources": {
                "default": True,
                "meshes": True
            },
            "enableDefaultSubsources": False
        },
        "precomputed://https://ngsupport-bmcp5imp6q-uk.a.run.app/neuronjson_segment_properties/fishemf-cleaving.janelia.org/c9df3e/segmentation_annotations/type/proposed_type",
        "precomputed://https://ngsupport-bmcp5imp6q-uk.a.run.app/neuronjson_segment_tags_properties/fishemf-cleaving.janelia.org/c9df3e/segmentation_annotations/type_user,proposed_type_user",
        {
            "url": "precomputed://https://ngsupport-bmcp5imp6q-uk.a.run.app/svmesh/fishemf-cleaving.janelia.org/c9df3e/segmentation_sv_meshes/body",
            "enableDefaultSubsources": False
        }

    ]

    img_source = {
        "type": "image",
        "source": {"url": "precomputed://gs://fish2-derived/em_sofima_240112",
                   "subsources": {"default": True},
                   "enableDefaultSubsources": False},
        "tab": "source",
        "name": "em-8nm"
    }

    position = (87523.453125, 56676.4609375, 5760.439453125)
    cross_section_scale = 13.5
    projection_scale = 56198.719452473684
    layout = "3d"

    # df contains: area, bodyId, DsColor
    def make_seg_layer(df, visible=True):
        df = df.dropna(subset=["bodyId"]).copy()
        df["bodyId"] = df["bodyId"].astype(int)

        segment_colors = {
            str(body_id): color
            for body_id, color in zip(df["bodyId"], df["color"])
            if isinstance(color, str) and color.startswith("#")
        }

        return {
            "type": "segmentation",
            "name": "layer_name",
            "source": seg_source,
            "segments": [str(x) for x in df["bodyId"].tolist()],
            "segmentColors": segment_colors,
            "visible": visible,
        }

    ng_layers = [
        img_source,
    ]

    ng_layers.append(make_seg_layer(df, visible=True))

    state = {
        "title": "Neurons",
        "dimensions": {"x": [8e-9, "m"], "y": [8e-9, "m"], "z": [3e-8, "m"]},
        "position": list(position),
        "crossSectionScale": cross_section_scale,
        "projectionScale": projection_scale,
        "layers": ng_layers,
        "layout": layout,
        "showSlices": False,
        "gpuMemoryLimit": 2_000_000_000,
        "systemMemoryLimit": 4_000_000_000,
    }

    payload = json.dumps(state, separators=(",", ":"))
    link = "https://clio-ng.janelia.org/#!" + urllib.parse.quote(payload, safe="")
    data = {"text": f"https://clio-ng.janelia.org/#!{urllib.parse.quote(payload, safe='')}", }

    r = requests.post("https://shortng-bmcp5imp6q-uc.a.run.app/shortng", json=data)
    # print(f"{r.json()['link']}")
    return f"{r.json()['link']}"


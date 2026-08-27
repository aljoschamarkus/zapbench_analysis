def dff(data, window, constant=1e-8):
    from scipy.ndimage import uniform_filter1d
    F0 = uniform_filter1d(data, size=window, axis=3, mode='nearest')
    dff = (data - F0) / (F0+constant)
    return dff

def janelia_neuroglancer_area(df):
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
    def make_seg_layer(name, df, visible=True):
        df_area = df[df["area"] == area]
        df_area = df_area.dropna(subset=["bodyId"]).copy()
        df_area["bodyId"] = df_area["bodyId"].astype(int)

        segment_colors = {
            str(body_id): color
            for body_id, color in zip(df_area["bodyId"], df_area["color"])
            if isinstance(color, str) and color.startswith("#")
        }

        return {
            "type": "segmentation",
            "name": name,
            "source": seg_source,
            "segments": [str(x) for x in df_area["bodyId"].tolist()],
            "segmentColors": segment_colors,
            "visible": visible,
        }

    ng_layers = [
        img_source,
    ]

    for area in df["area"].unique():
        ng_layers.append(make_seg_layer(area, df, visible=True))

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

def square_to_circle_vec(x, y):
    import numpy as np
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    u = np.full(x.shape, np.nan, dtype=float)
    v = np.full(y.shape, np.nan, dtype=float)

    valid = ~np.isnan(x) & ~np.isnan(y)
    nonzero = valid & ~((x == 0) & (y == 0))

    ax = np.abs(x)
    ay = np.abs(y)

    use_x = nonzero & (ax > ay)
    use_y = nonzero & ~use_x

    theta = np.empty_like(x, dtype=float)
    theta[:] = np.nan

    theta[use_x] = (np.pi / 4) * (y[use_x] / x[use_x])
    theta[use_y] = (np.pi / 2) - (np.pi / 4) * (x[use_y] / y[use_y])

    r = np.empty_like(x, dtype=float)
    r[:] = np.nan
    r[use_x] = x[use_x]
    r[use_y] = y[use_y]
    r[valid & (x == 0) & (y == 0)] = 0.0

    u[valid & (x == 0) & (y == 0)] = 0.0
    v[valid & (x == 0) & (y == 0)] = 0.0

    nz = nonzero
    u[nz] = r[nz] * np.cos(theta[nz])
    v[nz] = r[nz] * np.sin(theta[nz])

    return u, v

def hex_color(vx, vy, value=1.0):
    if vx == 0 and vy == 0:
        return None

    import numpy as np
    from matplotlib.colors import hsv_to_rgb, to_hex

    angle = np.arctan2(vx, vy) % (2 * np.pi)
    hue = (angle / (2 * np.pi) + 2 / 6) % 1.0

    rgb = hsv_to_rgb([hue, 1.0, value])
    return to_hex(rgb.tolist())
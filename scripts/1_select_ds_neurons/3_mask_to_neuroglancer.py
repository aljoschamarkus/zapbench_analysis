import numpy as np
import neuroglancer as ng
import tifffile
from config import *

PORT = 8080

ng.set_server_bind_address("127.0.0.1", PORT)

input_dimensions = ng.CoordinateSpace(
    names=["z", "y", "x", "c^"],
    units=["nm", "nm", "nm", ""],
    scales=[4000, 406, 406, 1],
)

output_dimensions = ng.CoordinateSpace(
    names=["x", "y", "z", "c^"],
    units=["nm", "nm", "nm", ""],
    scales=[406, 406, 4000, 1],
)

# maps input dimension (columns) on output dimensions (rows)
# last column corresponds to translation

matrix_mask = [
    [0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0],
    [1, 0, 0, 0, -1],
    [0, 0, 0, 1, 0]
]

spatial_dimensions = ng.CoordinateSpace(
    names=["x", "y", "z"],
    units=["nm", "nm", "nm"],
    scales=[406, 406, 4000],
)

matrix_mask_mike = [
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 0, 0, 0, -1],
    [0, 0, 0, 1, 0]
]

ds_map = None
if PATHS.in_tiff("ds_map.tif").exists():
    ds_map = tifffile.imread(PATHS.in_tiff("ds_map.tif")) # shape: (z, y, x, c)

ds_map_outline = None
if PATHS.in_tiff("ds_map_outlines.tif").exists():
    ds_map_outline = tifffile.imread(PATHS.in_tiff("ds_map_outlines.tif"))

colormapbigfull_flipped = None
if PATHS.in_tiff("colormapbigfull.tif").exists():
    colormapbigfull = tifffile.imread(PATHS.in_tiff("colormapbigfull.tif"))
    colormapbigfull_flipped = np.flip(colormapbigfull, axis=2)

colormapbigfull_outlines_flipped = None
if PATHS.in_tiff("colormapbigfull_outlines.tif").exists():
    colormapbigfull_outlines = tifffile.imread(PATHS.in_tiff("colormapbigfull_outlines.tif"))
    colormapbigfull_outlines_flipped = np.flip(colormapbigfull_outlines, axis=2)

VISIBLE = {
    "custom_map": False,
    "custom_map_outlines": False,
    "colormapbigfull": False,
    "colormapbigfull_outlines": True,
}

viewer = ng.Viewer()

with viewer.txn() as s:

    if ds_map is not None:
        s.layers["ds_map"] = ng.ImageLayer(
            source=ng.LayerDataSource(
                url=ng.LocalVolume(
                    data=ds_map,
                    dimensions=input_dimensions,
                    volume_type="image",
                ),
                transform=ng.CoordinateSpaceTransform(
                    matrix=matrix_mask,
                    output_dimensions=output_dimensions,
                ),
            ),
            shader="""
                void main() {
                  emitRGB(vec3(
                    toNormalized(getDataValue(0)),
                    toNormalized(getDataValue(1)),
                    toNormalized(getDataValue(2))
                  ));
                }
                """,
        )

    if ds_map_outline is not None:
        s.layers["ds_map_outlines"] = ng.ImageLayer(
            source=ng.LayerDataSource(
                url=ng.LocalVolume(
                    data=ds_map_outline,
                    dimensions=input_dimensions,
                    volume_type="image",
                ),
                transform=ng.CoordinateSpaceTransform(
                    matrix=matrix_mask,
                    output_dimensions=output_dimensions,
                ),
            ),
            shader="""
                void main() {
                  emitRGB(vec3(
                    toNormalized(getDataValue(0)),
                    toNormalized(getDataValue(1)),
                    toNormalized(getDataValue(2))
                  ));
                }
                """,
        )

    if colormapbigfull_flipped is not None:
        s.layers["colormapbigfull"] = ng.ImageLayer(
            source=ng.LayerDataSource(
                url=ng.LocalVolume(
                    data=colormapbigfull_flipped,
                    dimensions=input_dimensions,
                    volume_type="image",
                ),
                transform=ng.CoordinateSpaceTransform(
                    matrix=matrix_mask_mike,
                    output_dimensions=output_dimensions,
                ),
            ),
            shader="""
                void main() {
                  emitRGB(vec3(
                    toNormalized(getDataValue(0)),
                    toNormalized(getDataValue(1)),
                    toNormalized(getDataValue(2))
                  ));
                }
                """,
        )

    if colormapbigfull_outlines_flipped is not None:
        s.layers["colormapbigfull_outlines"] = ng.ImageLayer(
            source=ng.LayerDataSource(
                url=ng.LocalVolume(
                    data=colormapbigfull_outlines_flipped,
                    dimensions=input_dimensions,
                    volume_type="image",
                ),
                transform=ng.CoordinateSpaceTransform(
                    matrix=matrix_mask_mike,
                    output_dimensions=output_dimensions,
                ),
            ),
            shader="""
                void main() {
                  emitRGB(vec3(
                    toNormalized(getDataValue(0)),
                    toNormalized(getDataValue(1)),
                    toNormalized(getDataValue(2))
                  ));
                }
                """,
        )

    for name, visibility in VISIBLE.items():
        s.layers[name].visible = visibility

    # for name in LAYERS.keys():
    #     if LAYERS[name][1] == "image":
    #         s.layers[name] = ng.ImageLayer(
    #             source=ng.LayerDataSource(
    #                 url=LAYERS[name][0],
    #             ),
    #         )
    #     elif LAYERS[name][1] == "segmentation":
    #         s.layers[name] = ng.SegmentationLayer(
    #             source=ng.LayerDataSource(
    #                 url=LAYERS[name][0],
    #             ),
    #         )
    #     else:
    #         print("invalid")

    for name in LAYERS.keys():
        url = LAYERS[name][0]
        layer_type = LAYERS[name][1]
        visible = LAYERS[name][2]

        if layer_type == "image":
            layer = ng.ImageLayer(
                source=ng.LayerDataSource(url=url),
            )

        elif layer_type == "segmentation":
            layer = ng.SegmentationLayer(
                source=ng.LayerDataSource(url=url),
            )

        else:
            print("invalid")
            continue

        s.layers[name] = layer
        s.layers[name].visible = visible

    s.layers["annotations"] = ng.LocalAnnotationLayer(
        dimensions=spatial_dimensions,
    )

    s.position = [586, 675, 15]
    s.layout = "xy"

print(viewer)

input("stop server...")

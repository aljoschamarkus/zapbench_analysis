import numpy as np
import neuroglancer as ng
import tifffile
from pathlib import Path
from config import *

PORT = 8080

# host on device
ng.set_server_bind_address("127.0.0.1", PORT)

img = tifffile.imread(DS_MASK) # shape: (z, y, x, c)

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

img_mike_mask_flipped = None
matrix_mask_mike = None

if Path(DS_MASK_MIKE).exists():
    img_mike_mask = tifffile.imread(DS_MASK_MIKE)
    img_mike_mask_flipped = np.flip(img_mike_mask, axis=2)
    matrix_mask_mike = [
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 0, 0, 0, -1],
        [0, 0, 0, 1, 0]
    ]

viewer = ng.Viewer()

with viewer.txn() as s:

    s.layers["custom_mask"] = ng.ImageLayer(
        source=ng.LayerDataSource(
            url=ng.LocalVolume(
                data=img,
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

    if img_mike_mask_flipped is not None and matrix_mask_mike is not None:
        s.layers["mikes_mask"] = ng.ImageLayer(
            source=ng.LayerDataSource(
                url=ng.LocalVolume(
                    data=img_mike_mask_flipped,
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

    for name, url, variant, matrix, *_ in LAYERS:
        if variant == "image":
            s.layers[name] = ng.ImageLayer(
                source=ng.LayerDataSource(
                    url=url,
                    transform=ng.CoordinateSpaceTransform(
                        matrix=matrix,
                        output_dimensions=spatial_dimensions,
                    ),
                ),
            )
        elif variant == "segmentation":
            s.layers[name] = ng.SegmentationLayer(
                source=ng.LayerDataSource(
                    url=url,
                    transform=ng.CoordinateSpaceTransform(
                         matrix=matrix,
                        output_dimensions=spatial_dimensions,
                    ),
                ),
            )
        else:
            print("invalid")
    for name, *_, visible in LAYERS:
        s.layers[name].visible = visible

    s.layers["annotations"] = ng.LocalAnnotationLayer(
        dimensions=spatial_dimensions,
    )

    s.position = [586, 675, 15]
    s.layout = "xy"

print(viewer)

input("stop server...")

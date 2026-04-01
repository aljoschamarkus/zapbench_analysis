import numpy as np
import neuroglancer as ng
import tifffile

VOLUME_LIMS = {
    "x_min": 430,
    "x_max": 710,
    "y_min": 500,
    "y_max": 810,
    "z_min": 6,
    "z_max": 19,
}

vol = np.zeros((72, 1328, 2048, 3), dtype=np.uint8)
roi = np.ones((13, 310, 280, 3), dtype=np.uint8) * 255
vol[
    VOLUME_LIMS["z_min"]:VOLUME_LIMS["z_max"],
    VOLUME_LIMS["y_min"]:VOLUME_LIMS["y_max"],
    VOLUME_LIMS["x_min"]:VOLUME_LIMS["x_max"],
    :
] = roi


PORT = 8080
ng.set_server_bind_address("127.0.0.1", PORT)
path = "/Users/aljoscha/Downloads/zapbench_data_thalamus/colormapbigfull.tif"

img_mike_mask = tifffile.imread(path)
img_mike_mask_flipped = np.flip(img_mike_mask, axis=2)

img_mask = vol

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

matrix_mask_mike = [
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 0, 0, 0, -1],
    [0, 0, 0, 1, 0]
]

matrix_mask = [
    [0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0],
    [1, 0, 0, 0, -1],
    [0, 0, 0, 1, 0]
]

viewer = ng.Viewer()

with viewer.txn() as s:

    s.layers["mike_mask"] = ng.ImageLayer(
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

    s.layers["roi_mask"] = ng.ImageLayer(
        source=ng.LayerDataSource(
            url=ng.LocalVolume(
                data=img_mask,
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

    s.position = [586, 675, 15]
    s.layout = "xy"

print(viewer)

input("stop server...")

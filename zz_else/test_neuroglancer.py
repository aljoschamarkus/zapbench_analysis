import numpy as np
import neuroglancer as ng
import tifffile

PORT = 8080
ng.set_server_bind_address("127.0.0.1", PORT)
path = "/Users/aljoscha/Downloads/zapbench_data_thalamus/colormapbigfull.tif"

img_mike_mask = tifffile.imread(path)
img_mike_mask_flipped = np.flip(img_mike_mask, axis=2)

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

    s.position = [0, 0, 0]
    s.layout = "xy"

print(viewer)

input("stop server...")

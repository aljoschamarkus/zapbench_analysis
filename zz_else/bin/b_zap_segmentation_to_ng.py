import tensorstore as ts
import numpy as np
from config import *
import scipy.ndimage as sciimg
from pathlib import Path
import tifffile

def img_to_ng(layers):
    import neuroglancer as ng
    from numpy import min, max
    PORT = 8080
    ng.set_server_bind_address("127.0.0.1", PORT)

    in_dimensions = ng.CoordinateSpace(
        names=["x", "y", "z"],
        units=["nm", "nm", "nm"],
        scales=[406, 406, 4000],
    )

    out_dimensions = ng.CoordinateSpace(
        names=["x", "y", "z"],
        units=["nm", "nm", "nm"],
        scales=[406, 406, 4000],
    )

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

    spatial_dimensions = ng.CoordinateSpace(
        names=["x", "y", "z"],
        units=["nm", "nm", "nm"],
        scales=[406, 406, 4000],
    )

    matrix = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, -1],
    ]
    matrix2 = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
    ]

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
        for name, img in layers.items():
            img_scaled = (img-min(img))/(max(img)-min(img))
            binary = (img_scaled != 0).astype(np.uint32)

            s.layers[name] = ng.SegmentationLayer(

                source=ng.LayerDataSource(
                    url=ng.LocalVolume(
                        data=binary,
                        dimensions=in_dimensions,
                        volume_type='segmentation',  # make it explicit
                    ),
                    transform=ng.CoordinateSpaceTransform(
                        matrix=matrix,
                        output_dimensions=out_dimensions,
                    ),
                ),
                hide_segment_zero=True,
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

        s.layers["segmentation"] = ng.SegmentationLayer(
            source=ng.LayerDataSource(
                url="gs://zapbench-release/volumes/20240930/segmentation_xy_multiscale/|zarr3:",
                transform=ng.CoordinateSpaceTransform(
                    matrix=matrix2,
                    output_dimensions=spatial_dimensions,
                ),
            ),
        )

        s.layers["segmentation"].visible = True
        s.layout = "xy"

    print(viewer)
    input("stop server...")

# "gs://zapbench-release/volumes/20240930/segmentation_xy_multiscale/|zarr3:"
ds = {
    'open': True,
    'driver': 'zarr3',
    'kvstore': "gs://zapbench-release/volumes/20240930/segmentation_xy"
}

ds_ts = ts.open(ds, open=True).result()
ds_subsample = ds_ts[:, :, :].read().result()

# ds_dilated = sciimg.binary_dilation(ds_subsample, axes=(0, 1))
footprint = np.array([
    [0,1,0],
    [1,1,1],
    [0,1,0]
], dtype=bool)

ds_dilated = sciimg.grey_dilation(ds_subsample, footprint=footprint, axes=(0, 1))
ds_substracted = ds_subsample - ds_dilated

print(ds_substracted.max())
layers = {"name": ds_substracted}
img_to_ng(layers)
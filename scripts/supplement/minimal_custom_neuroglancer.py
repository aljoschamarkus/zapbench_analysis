import neuroglancer as ng

PORT = 8080

ng.set_server_bind_address("127.0.0.1", PORT)

viewer = ng.Viewer()

with viewer.txn() as s:
    s.layers["zap_anatomy"] = ng.ImageLayer(
        source=ng.LayerDataSource(
            url="gs://zapbench-release/volumes/20240930/anatomy_clahe_ds_multiscale/|zarr3:",
        ),
    )

    s.position = [586, 675, 15]
    s.layout = "xy"

print(viewer)

input("stop server...")

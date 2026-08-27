from pathlib import Path

class Paths:
    def __init__(self, base: Path, create: bool=True):
        self.base = base
        self.data = base / "data"
        self.tiff = base / "tiff_stacks"
        self.neurons = base / "neuron_tables"
        self.plots = base / "plots"

        if create:
            self._create_dirs()

    def _create_dirs(self):
        for path in [
            self.base,
            self.data,
            self.tiff,
            self.neurons,
            self.plots,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def in_data(self, name):
        return self.data / name
    def in_tiff(self, name):
        return self.tiff / name
    def in_neurons(self, name):
        return self.neurons / name
    def in_plots(self, name):
        return self.plots / name

main_dir = "/Users/aljoscha/Downloads/fish22"

PATHS = Paths(Path(main_dir))

GS = {
    "zap_stimuli": ['zarr', 'gs://zapbench-release/volumes/20240930/stimuli_features'],
    "zap_aligned": ['zarr3', 'gs://zapbench-release/volumes/20240930/aligned'],
    "zap_segmentation": ['zarr3', "gs://zapbench-release/volumes/20240930/segmentation_xy"],
    "zap_traces": ['zarr3', 'gs://zapbench-release/volumes/20240930/traces'],
    "zap_mece_pretectum": ['neuroglancer_precomputed', 'gs://fish2-derived/mece_250317/mece2'],
    "fish1_somas": ['neuroglancer_precomputed', 'gs://fish1-public/lores_cbs_231218'],
    "fish1_nt": ['n5', 'gs://fish1-public/confocal_231218.n5/s0'],
}

LAYERS = {
    "zap_segmentation": ["gs://zapbench-release/volumes/20240930/segmentation_xy_multiscale/|zarr3:", "segmentation", False],
    "zap_anatomy": ["gs://zapbench-release/volumes/20240930/anatomy_clahe_ds_multiscale/|zarr3:", "image", False],
}

# Exmaple Data

url_fish2_thalamic = "https://docs.google.com/spreadsheets/d/13QOqf9SwgmFEzKOpOkgT1OJyPlZ-wxlZ5IZdEuoR2ag/export?format=csv&gid=0"
url_fish1_pretectal = "https://docs.google.com/spreadsheets/d/13QOqf9SwgmFEzKOpOkgT1OJyPlZ-wxlZ5IZdEuoR2ag/export?format=csv&gid=1140184864"

VOLUME_LIMS = {
    "x_min": 430,
    "x_max": 710,   # exclusive
    "y_min": 500,
    "y_max": 810,   # exclusive
    "z_min": 6,
    "z_max": 19,    # exclusive
}

THALAMIC_EM_IDS = [100459637, 100489572, 100554843, 100606891, 100872084, 100960836, 101375512, 101655767, 101905119, 102763559, 104512644, 105340332, 106132947, 106196373, 109686908]



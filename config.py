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

VOLUME_LIMS = {
    "x_min": 430,
    "x_max": 710,   # exclusive
    "y_min": 500,
    "y_max": 810,   # exclusive
    "z_min": 6,
    "z_max": 19,    # exclusive
}

VOLUME_LIMS_2 = {
    "x_min": 520,
    "x_max": 620,   # exclusive
    "y_min": 675,
    "y_max": 775,   # exclusive
    "z_min": 10,
    "z_max": 14,    # exclusive
}

# main_dir = "/Users/aljoscha/Downloads/fish2"
main_dir = "/Users/aljoscha/Downloads/fish22"

PATHS = Paths(Path(main_dir))

THALAMIC_DS_ZAP_ID = [
7556,
19975,
21691,
21516,
20026,
7638,
7556,
8972,
8972,
8986,
20085,
19883,
8914,
19893,
21484,
7638,
21513,
8969,
8999,
31816,
7715,
8925,
8938,
8924,
7589,
8925,
19878,
21508,
21697,
19975,
21506,
21490,
8924,
19806,
8925,
19767,
21452,
7650,
21644,
19883,
19893,
19878
]



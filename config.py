import os

MAIN_DIR = "/Users/aljoscha/Downloads/zapbench_data"
STIM_FILE = os.path.join(MAIN_DIR, "stim.h5")
DATA_DIR = os.path.join(MAIN_DIR, "zapbench_aligned")
TIF_FILE = os.path.join(MAIN_DIR, "activity_mask.tif")

VOLUME_LIMS = {
    "x_min": 700,
    "x_max": 951,
    "y_min": 450,
    "y_max": 851,
    "z_min": 15,
    "z_max": 36,
}

TRANSFORMATION_MATRIX = [
    [1,0,0,-450],
    [0,1,0,-450],
    [0,0,-1,74],
]
NULL_TRANSFORM = [
    [1,0,0,0],
    [0,1,0,0],
    [0,0,1,0],
]

LAYERS = [
    ["zap_bench_segmentation", "gs://zapbench-release/volumes/20240930/segmentation_xy_multiscale/|zarr3:", "segmentation", NULL_TRANSFORM],
    ["zapbench_anatomy", "gs://zapbench-release/volumes/20240930/anatomy_clahe_ds_multiscale/|zarr3:", "image", NULL_TRANSFORM],
    ["em_8nm", "precomputed://gs://fish2-derived/em_sofima_240112", "image", TRANSFORMATION_MATRIX],
    ["brain_shell", "precomputed://gs://fish2-derived/fish2-brain-shell", "segmentation", TRANSFORMATION_MATRIX],
    ["mece0", "precomputed://gs://fish2-derived/mece_250317/mece0", "segmentation", TRANSFORMATION_MATRIX],
    ["mece1", "precomputed://gs://fish2-derived/mece_250317/mece1", "segmentation", TRANSFORMATION_MATRIX],
    ["mece2", "precomputed://gs://fish2-derived/mece_250317/mece2", "segmentation", TRANSFORMATION_MATRIX],
    ["mece3", "precomputed://gs://fish2-derived/mece_250317/mece3", "segmentation", TRANSFORMATION_MATRIX],
]

# to test sample comment above and uncomment below
# Runtime estimate:
#   scripts/1_get_stimulus_data.py ~1min
#   scripts/2_download_functional_imaging.py ~1min
#   scripts/3_create_activity_mask.py ~0sec
#   scripts/4_mask_to_neuroglancer.py ~0sec

# MAIN_DIR = "/Users/aljoscha/Downloads/zapbench_data_test"
# STIM_FILE = os.path.join(MAIN_DIR, "stim.h5")
# DATA_DIR = os.path.join(MAIN_DIR, "test")
# TIF_FILE = os.path.join(MAIN_DIR, "test.tif")
# VOLUME_LIMS = {
#     "x_min": 700,
#     "x_max": 704,
#     "y_min": 450,
#     "y_max": 454,
#     "z_min": 24,
#     "z_max": 27,
# }


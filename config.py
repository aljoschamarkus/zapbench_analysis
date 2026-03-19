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
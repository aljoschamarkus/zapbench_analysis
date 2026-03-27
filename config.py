import os

MAIN_DIR = "/Users/aljoscha/Downloads/zapbench_data_thalamus"
STIM_FILE = os.path.join(MAIN_DIR, "stim.h5")
DATA_DIR = os.path.join(MAIN_DIR, "zapbench_aligned")
DATA_FILE = os.path.join(MAIN_DIR, "zapbench_aligned.h5")
TIF_FILE = os.path.join(MAIN_DIR, "activity_mask.tif")
MASK_MIKE = os.path.join(MAIN_DIR, "colormapbigfull.tif")
CSV_FILE = os.path.join(MAIN_DIR, "annotations.csv")

VOLUME_LIMS = {
    "x_min": 430,
    "x_max": 710,
    "y_min": 500,
    "y_max": 810,
    "z_min": 6,
    "z_max": 19,
}

# VOLUME_LIMS = {
#     "x_min": 700,
#     "x_max": 951,
#     "y_min": 450,
#     "y_max": 851,
#     "z_min": 15,
#     "z_max": 36,
# }

NULL_TRANSFORM = [
    [1,0,0,0],
    [0,1,0,0],
    [0,0,1,0],
]

TRANSFORMATION_MATRIX_EM = [
    [1,0,0,-450],
    [0,1,0,-450],
    [0,0,-1,74],
]

LAYERS = [
    # naturally aligned comes from same imaging
    ["zap_bench_segmentation", "gs://zapbench-release/volumes/20240930/segmentation_xy_multiscale/|zarr3:", "segmentation", NULL_TRANSFORM, False],
    ["zapbench_anatomy", "gs://zapbench-release/volumes/20240930/anatomy_clahe_ds_multiscale/|zarr3:", "image", NULL_TRANSFORM, False],
    # bad alignment
    # ["em_8nm", "precomputed://gs://fish2-derived/em_sofima_240112", "image", TRANSFORMATION_MATRIX_EM, False],
    # ["brain_shell", "precomputed://gs://fish2-derived/fish2-brain-shell", "segmentation", TRANSFORMATION_MATRIX_EM, False],
    # ["mece0", "precomputed://gs://fish2-derived/mece_250317/mece0", "segmentation", TRANSFORMATION_MATRIX_EM, False],
    # ["mece1", "precomputed://gs://fish2-derived/mece_250317/mece1", "segmentation", TRANSFORMATION_MATRIX_EM, False],
    # ["mece2", "precomputed://gs://fish2-derived/mece_250317/mece2", "segmentation", TRANSFORMATION_MATRIX_EM, False],
    # ["mece3", "precomputed://gs://fish2-derived/mece_250317/mece3", "segmentation", TRANSFORMATION_MATRIX_EM, False],
]

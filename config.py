import os

MAIN_DIR = "/Users/aljoscha/Downloads/zapbench_data_thalamus"

STIM_H5 = os.path.join(MAIN_DIR, "stim.h5")

FUNCTIONAL_IMG_DIR = os.path.join(MAIN_DIR, "zapbench_aligned")
FUNCTIONAL_IMG_H5 = os.path.join(MAIN_DIR, "zapbench_aligned.h5")

DS_MASK = os.path.join(MAIN_DIR, "activity_mask.tif")
DS_MASK_MIKE = os.path.join(MAIN_DIR, "colormapbigfull.tif")

TRACES_H5 = os.path.join(MAIN_DIR, "zapbench_traces.h5")
ZAP_DS_H5 = os.path.join(MAIN_DIR, "zap_ds.h5")

NEUPRINT_NEURONS_CSV = os.path.join(MAIN_DIR, "ds_neurons.csv")

ACTIVITY_CORRELATION_H5 = os.path.join(MAIN_DIR, "rois.h5")

VOLUME_LIMS = {
    "x_min": 430,
    "x_max": 710,   # exclusive
    "y_min": 500,
    "y_max": 810,   # exclusive
    "z_min": 6,
    "z_max": 19,    # exclusive
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

PRETECTAL_DS_ZAP_ID = [
22400,
22179,
32767,
22145,
22145,
24239,
22361,
22361,
22343,
22343,
22353,
22342,
9739,
10183,
9797,
9831,
9573,
9573,
9648,
11559,
9465,
9481,
9486,
9525,
9546,
9572,
9625,
9627,
9762,
22006,
22020,
22336,
22356,
22360,
22428,
22499,
24127,
32743,
9465,
9481,
9486,
9525,
9546,
9572,
9625,
9627,
9762,
22006,
22020,
22336,
22356,
22360,
22428,
22499,
24127,
32743
]

NEURONS_DS_ZAP_ID = {
    "Thalamus": set(THALAMIC_DS_ZAP_ID),
    "Pretectum": set(PRETECTAL_DS_ZAP_ID),
}
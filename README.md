# Direction selective thalamic circuits - Larval zebrafish 

This projects analyses direction selectivity in the zebrafish visual thalamus based on electron microscopy and [functional imaging](google-research.github.io/zapbench) datasets

## Requirements
- [**Neuprint authorization key**](https://neuprint-fish2.janelia.org/account)
- [**fishFuncEM package**](https://github.com/ahrens-fish-lab/fishFuncEM.git)

## Installation
```bash
git clone https://github.com/aljoschamarkus/zapbench_analysis.git
```

## Data sets

The data for the analysis in this project is from the following sources, the  Google Storage URIs can be found in [`config.py`](./config.py)

- [**ZAPBench**](google-research.github.io/zapbench): whole brain functional GCaMP imaging ([published](https://doi.org/10.48550/arXiv.2503.02618), data open source)
  - Stimuli data
  - Aligned activity volume
  - Segmentation of neurons
  - Traces of activity for segments
- [**Fish2 EM (neuPrint)**](https://neuprint.janelia.org/): electron microscopy dataset (unpublished, authorization key required)
  - Mece 2 mask
  - Segmentation
  - Connectivity
- [**Fish1 EM (CAVE)**](https://fish1-release.storage.googleapis.com/index.html): electron microscopy dataset ([published](https://doi.org/10.1101/2025.06.10.658982), test data available full dataset requires CAVE account)
  - Segmentation
  - Confocal imaging (*vglut2a* / *gad1b*)

| name                   | shape             | dimensions       | units                        | driver                   |
|------------------------|-------------------|------------------|------------------------------|--------------------------|
| [Stimuli](./config.py) | 7879x26           | time, channels   | 914 ms, -                    | zarr                     |
| Aligned                | 2048x1328x72x7879 | x, y, z, time    | 406 nm, 406 nm, 4 µm, 914 ms | zarr3                    |
| Segmentation           | 2048x1328x72      | x, y, z          | 406 nm, 406 nm, 4 µm         | zarr3                    |
| Traces                 | 7879x71721        | time, neurons    | 914 ms, -                    | zarr3                    |
| Mece 2 mask            | 3200x1792x641x1   | x, y, z, channel | 512 nm, 512 nm, 480 nm, -    | neuroglancer_precomputed |
| Somas                  | 2100x1016x8689x2  | x, y, z, channel | 512 nm, 512 nm, 30 nm, -     | neuroglancer_precomputed |
| Confocal               | 2100x1016x8689x2   | x, y, z, channel | 512 nm, 512 nm, 30 nm, -     | n5                       |

## Directory structure

```
|-fish2
|   |-data
|   |   |-zap_stimulus_turning.h5
|   |   |-zap_aligned_slices
|   |   |   |-zap_aligned_slice_0.h5
|   |   |   |-[...]
|   |   |-zap_aligned_volume.h5
|   |   |-zap_traces.h5
|   |   |-zap_mece_pretectum.h5
|   |-tiff_stacks
|   |   |-ds_mask_custom.tif
|   |   |-ds_mask_zap_outlines.tif
|   |   |(-colormapbigfull.tif)
|   |   |(-colormapbigfull_outlines.tif)
|   |-neuron_tables
|   |   |-df_neurons.csv
|   |   |-[...]
|   |-plots
|   |    |-plot_1.png
|   |    |-[...]
```

## Introduction

Use EM and functional imaging to disect direction selectivity computation on the circuit level

Sabines work -> topographic map of direction selectivity in the thalamus

previously known that af5 direction selective

flow of information: RGC -> AF5 -> Pretectum -> Thalamus

### 1. Finding direction selective neurons 

To determine direction selectivity the functional imaging during the "Turning" stimulus of ZAPBench was used.
The stimulus consists of sine gratings drifting into the four cardinal directions (open loop).
Every direction was shown for 30s followed by a 30s inter stimulus interval of stationary gratings.
This was repeated 5 times.<br>

The aligned activity volume was divided in 5 time bins combining periods of gratings from a particular direction as well as the inter stimulus interval.
The $\text{response}$ of a voxel towards a directional stimulus was quantified as the mean activity during a time bin subtracted by the mean of the inter stimulus interval bin as a baseline

$$
\text{response}_{\text{dir}} =
\frac{
\sum_{t_{\text{stim}}=1}^{n_{\text{stim}}} \text{activity}_{t_{\text{stim}}}
}
{
n_{\text{stim}}}
-\frac{
\sum_{t_{\text{off}}=1}^{n_{\text{off}}} \text{activity}_{t_{\text{off}}}
}
{
n_{\text{stim}}
}$$

From the responses towards the 4 stimulus directions a vector was calculated by subtracting opposing directions in the same dimension.
The direction $\theta$ of the vector encodes the direction of selectivity and its length the $\text{magnitude}$.

$$
\mathbf{v} =
(
\text{response}_{\text{right}} - \text{response}_{\text{left}},
\text{response}_{\text{forward}} - \text{response}_{\text{backward}}
)
$$

$$
\theta = \mathrm{atan2}(x,y) \bmod 2\pi
$$

$$
\text{magnitude} = \sqrt{x^2 + y^2} $$

For visualisation tiff volume was created in which the color encoded direction selectivity.
The hue encodes the direction as shown below, the value encodes the magnitude, scaled by the 99th percentile, as a linear function and the saturation was constant at 1.
<br>

$$\text{hue}=(\frac{\theta}{2\pi}+2/6)\bmod 1$$

**Note:** Since the value is scaled by the percentile of direction selectivity magnitude of the voxel population, the colors for the same voxels can slightly vary when the calculation is done on differnet sub volumes.

<p align="center">
  <img src="pngs/mask.png" alt="mask" width="200">
  <img src="pngs/mask_out.png" alt="mask_out" width="200">
</p>

For easier selection of ZAPBench neuron segmentations a copy of the tiff volume was stored with white outlines around soma masks from the segmentation dataset.
This was done by subtracting the segment masks from the dilated version of it, to avoid dilation of merged ROIs this was done per segment ID. The resulting outlines were then combined and corresponding voxel colors in the tiff volume are set to white.<br>

Both masks can be loaded into neuroglancer tab that is locally hosted and allows implementing local and nonlocal volumes.
By overlaying the custom direction selectivity map with the ZAPBench segmentation, segments can be selected and IDs copied.

### 2. Analysing neuronal morphology

After selecting ZAPBench neurons of the desired area and direction selectivity with their IDs their direction selectivity parameters can be extracted directly from the traces dataset.
Direction and color was determined as above but with activity traces instead of voxel brightness.

Since the vector logic above only taking into account the sparse sampling of 4 directions, the vectors can fill a square space with the $x$ and $y$ limits being $\pm$maximum response.
To not over represent the direction selectivity for high responses towards two cardinal directions the vectors were mapped to a circular space to quantify magnitude to represent selectivity more accurately.

$$
r = \max(|x|, |y|)
$$


$$(x_{\text{circ}}, y_{\text{circ}})=(r\sin(\theta), r\cos(\theta))$$

$$
\text{magnitude}_{\text{circ}} = \sqrt{x_{\text{circ}}^2 + y_{\text{circ}}^2} $$

In the neuprint database via cypher query the ZAPBench IDs can be mapped to EM segmentation IDs and additional information such as the side can be extracted.
To analyse morphology the neurons can be loaded and viewed in a clio neuroglancer tab, here the same color coding by direction selectivity is implemented.
The selection can therefor be refined taking morphology and projection patterns into account.

<p align="center">
  <img src="pngs/em_ng_thalamus.png" alt="mask_out" width="600">
</p>

### 3. Analysing circuit characteristics

To analyse the characteristics of the neural connections for a better understanding of the circuit calculations giving rise to direction selectivity the relation of direction selectivity of connected neurons can determined.<br>

As potential inputs here based on the Mece 2 Pretectum mask the IDs of all pretectal neurons were extracted.
For better performance in a first step all neuron IDs within a bounding box based on the minimum and maximum position of maks voxels, were determined by query in neuprint.
Afterwards based on position membership of the pretectal mask was tested while only members were kept.

Another query outputs direct axon to dendrite connections between the listed upstream and downstream neuron IDs.
The cosine similarity between the direction selectivity vector of up- and downstream neurons of the same and of opposite sides was calculated.
A cosine similarity of 1 represents identical, 0 to orthogonal and -1 to opposite direction.

$$\text{cosine similarity}=\frac{A \cdot B}{||A||\text{ }||B||}=
\frac{x_{1_{\text{circ}}}x_{2_{\text{circ}}}+y_{1_{\text{circ}}}y_{2_{\text{circ}}}}
{\sqrt{x_{1_{\text{circ}}}^2+y_{1_{\text{circ}}}^2}\sqrt{x_{2_{\text{circ}}}^2+y_{2_{\text{circ}}}^2}}$$

<p align="center">
  <img src="pngs/cos_sim_threshold.png" alt="mask_out" width="400">
</p>

Unlike for fish2 data for fish1 confocal imaging of genetic labels of *vglut2a* and *gad1b* indicates excitatory or inhibitory identity of the neurons.
For a subpopulation of pretectal neurons, that were selected to have dendritic projections into AF5 the relation of contra- and ipsilateral connections and the neurotransmitter has been quantified.

Though the CAVE database contains information about transmitter identity, the labeling is very sparse and for most neurons is available.
After manually determining neurotransmitter identity an automatic readout of neurotransmitter was implemented.   
For that the difference over sum ratio of mean *vglut2a* and mean *gad1b* expression was determined and a $\pm$threshold everything below the threshold is not classified while absolute values above were classified accordingly.
With a threshold of 0.4 this method had not a single disagreement with both CAVE labels and manual selection while being much more sensitive. 

$$I_{\text{exc}}=
\frac{\bar{a}_{\text{glut}}-\bar{a}_{\text{gaba}}}
{\bar{a}_{\text{glut}}+\bar{a}_{\text{gaba}}}$$

<p align="center">
  <img src="pngs/bar_chart.png" alt="mask_out" width="400">
</p>

## Usage

### 1. Select direction selective neurons


## Achievements

custom volume to ng
manual selection of ds neurons (colormap)
color coding based on traces (to ng as well)

manual selection pretectal em?

automatic quantification confocal mask (better resolution then CAVE data)

Share google sheet fish1 pretectal
maybe indication of proofreading

share fish2 thalamic neurons


where are those neurones how to infer functionality (ds)


To infer 


final:

by combining direction selectivity information of functional imaging (zap) with anatomy and connectivity (fish2 em) and neurotranmitter identity/ indication of excitatory or inhibitory from the confocal imaging (fish1) population of neurons of particular anatomy, flow of information and circuit schema could be found

## Notes:
Data introduction
Goal introduction
Project structure introduction
deutilise
Requirements pip install
Jupyter notebook
Batch attempt
Estimated storage
Estimated runtime
Make layers invisible
Add exploratory test namely
Filtering spatialy
Threshold ds
reference lines?
reference Aarons cave query
pipeline schema

### colormap
- Note hue scaling is dependent on percentile of brightness value so for volume limits the absolute rgb values of the tiff might vary!

### fish1
- Bounding box (optional)
- 

#### general

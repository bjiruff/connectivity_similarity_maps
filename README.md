# Overview
Code used to generate connectivity similarity heatmaps shown in Figures 5A, B, Supplementary Figure S5A-C in the manuscript entitled "*Cellular and functional dissection of the octopaminergic system in the Drosophila brain*" (Palacios Castillo, L.M., Fajner, V. et al., 2026). It uses fly brain connectomes to vectorize connectivity information for a specified list of cell types. Vector similarity metric used is cosine similarity.
# Setup Instructions
## 1. Obtaining Connectome Data
Raw connectome data must be obtained from various sources. Place all downloaded .csv and .feather files in `data/raw/`.
### FAFB
From https://codex.flywire.ai/api/download?dataset=fafb, obtain:
- consolidated_cell_types.csv
- classification.csv
- connections_princeton.csv
### MCNS
From https://male-cns.janelia.org/download/, obtain:
- body-annotations-male-cns-v0.9-minconf-0.5.feather
- connectome-weights-male-cns-v0.9-minconf-0.5.feather
### MANC
At the time of writing, a download catalog for MANC 1.2.1 does not exist. MANC data was instead obtained using neuprint-python's API. Obtain an authorization token [here](https://connectome-neuprint.github.io/neuprint-python/docs/quickstart.html#quickstart), and within `scripts/convert_manc`, paste your token. 
## 2. Converting Connectome Data
Upon obtaining the necessary files, the raw datasets need to be converted to a common format. Run `convert_all.py` to do so. Then, you can begin making the similarity maps in `analysis.ipynb`.
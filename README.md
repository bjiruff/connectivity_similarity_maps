# Overview
Code used to generate Figures 5A–D, 5K, and 5L, and Supplementary Figures S5A-F in the manuscript entitled "*Cellular and functional dissection of the octopaminergic system in the Drosophila brain*" (Palacios Castillo, L.M., Fajner, V. et al., 2026).
# Setup Instructions
## 1. Environment Setup
Assuming that you have Python (>=3.11), you can run `pip install -e .` from the root directory to install the project and its dependencies. 
## 2. Obtaining Connectome Data
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
At the time of writing, a download catalog for MANC 1.2.1 does not exist. MANC data was instead obtained using neuprint-python. Obtain an authorization token [here](https://connectome-neuprint.github.io/neuprint-python/docs/quickstart.html#quickstart), run `cp .env.example .env` and paste your token.
## 3. Converting Connectome Data
Upon obtaining the necessary files, the raw datasets need to be converted to a common format. Run `python scripts/convert_datasets.py` to do so.
# Figure Generation
In `scripts/`, `plot_similarity_matrix.py` makes Figures 5A-B, S5A-B, S5E-F. `plot_dendrogram.py` makes Figures 5A-D, S5A-B, S5E-F. `plot_shared_partners.py` makes Figures 5K-L, S5C-D. Outputs are made to `savefigs/`.



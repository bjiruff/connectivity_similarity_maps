import plotly.express as px
import proj.processing.connectivity as c
import proj.plotting.sim_map as sm
from proj.config.consts import OA_FAFB, OA_MCNS, OA_MANC
from proj.config.paths import SAVEFIGS_DIR

def main():
    """Plot similarity matrix seen in figures ...."""
    dataset = "manc" # Specify from which connectome to pull OA neuron data from. 'fafb', 'mcns', or 'manc'.
    direction = "upstream" # Specify if you want to find 'upstream', 'downstream', or 'combined' upstream+downstream similarities.
    plot_dim = 800 # Set width and height of similarity plot. Recommend 800 for manc and 2000 for fafb/mcns.

    datasets = ["fafb", "mcns", "manc"]
    directions = ["upstream", "downstream", "combined"]

    if dataset not in ["fafb", "mcns", "manc"]:
        raise ValueError(f"dataset must be {datasets}")
    if direction not in directions:
        raise ValueError(f"direction must be in {directions}")


    dataset_to_oa = {
        "fafb": OA_FAFB,
        "mcns": OA_MCNS,
        "manc": OA_MANC,
    }

    # For OA neurons (n), get synapse counts with the union of all their partners (m) and store in nxm matrix.
    connectivity_matrix = c.get_connectivity_matrix(cell_types=dataset_to_oa[dataset], dataset=dataset)

    # Consider only upstream or downstream connections.
    if direction == "upstream":
        connectivity_matrix = connectivity_matrix.loc[:, connectivity_matrix.columns.get_level_values("direction") == "upstream"]
    elif direction == "downstream":
        connectivity_matrix = connectivity_matrix.loc[:, connectivity_matrix.columns.get_level_values("direction") == "downstream"]

    # Store cosine similarities among OA neurons' connectivity vectors in nxn matrix.
    similarity_matrix = sm.get_connectivity_similarity(connectivity_matrix)

    labels = c.get_labels(similarity_matrix)

    # Plot.
    fig = px.imshow(
        similarity_matrix,
        x=labels,
        y=labels,
        color_continuous_scale="Oranges",
        zmin=0,
        zmax=1,
        aspect="equal",
        height=plot_dim,
        width=plot_dim,
    )

    fig.write_html(str(SAVEFIGS_DIR / f"{dataset}_{direction}_similarity_matrix.html"))

if __name__ == "__main__":
    main()
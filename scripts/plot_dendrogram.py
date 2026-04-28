import proj.processing.connectivity as c
import proj.plotting.dendro as d
from proj.config.consts import OA_FAFB, OA_MCNS, OA_MANC
from proj.config.paths import SAVEFIGS_DIR

def main():
    """Plot dendrogram and elbow method. Figures 5A-D, S5A-B, S5E-F."""

    dataset = "fafb" # Specify from which connectome to pull OA neuron data from. 'fafb', 'mcns', or 'manc'.
    direction = "downstream" # Specify if you want to find 'upstream', 'downstream', or 'combined' upstream+downstream similarities.

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

    link = d.get_linkage(connectivity_matrix)

    fig = d.plot_diagnostics(connectivity_matrix, link)
    fig.suptitle(f"{dataset} {direction} UPGMA clustering")
    fig.tight_layout()
    fig.savefig(str(SAVEFIGS_DIR / f"{dataset}_{direction}_dendrogram.png"), dpi=300)

if __name__ == "__main__":
    main()
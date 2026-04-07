import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
import proj.processing.connectivity as c
from proj.config.consts import OA_FAFB, OA_MCNS, OA_MANC

def get_linkage(mat):
    """Get linkage matrix for OA neurons based on shared connectivity."""
    method = "average"
    metric = "cosine"

    link = linkage(mat, method=method, metric=metric)

    return link
    

def plot_elbow(link, merge_ax=None, accel_ax=None):
    """Plot elbow plot to estimate the optimal k for dendrogram."""
    if merge_ax is not None and accel_ax is not None:
        fig = merge_ax.get_figure()
    else:
        fig, (merge_ax, accel_ax) = plt.subplots(2, 1, figsize=(8, 6))
    

    merges = np.insert(link[:, 2], 0, 0) # Get merge distances at each merge step.
    max_k = len(merges)
    k_range = range(max_k)
    inv_k_range = lambda x: max_k - x

    tick_step = 10
    xticks = range(0, max_k, tick_step)
    inv_xticks = range(max_k, 0, -tick_step)

    accel = np.diff(merges, 2)
    elbow_idx = accel.argmax() + 1
    optimal_k = max_k - elbow_idx

    # Merge distances.
    merge_ax_ylim = (0, 1)
    merge_ax.plot(k_range, merges, marker="o", color="steelblue")
    merge_ax.axvline(x=elbow_idx, color="red", linestyle="--", label=f"k={optimal_k}")
    merge_ax.set_xlim(k_range[0], k_range[-1])
    merge_ax.set_ylim(*merge_ax_ylim)
    merge_ax.set_ylabel("Merge Distance")

    sec_merge_ax = merge_ax.secondary_xaxis("top", functions=(inv_k_range, inv_k_range))
    sec_merge_ax.set_xlabel("# Clusters (k)")
    sec_merge_ax.set_xticks(inv_xticks)
    merge_ax.set_xticks([])
    merge_ax.legend()

    # Second derivative.
    accel_ax_ylim = (-0.5, 0.5) # Might have to increase range for cases where acceleration is very high.
    accel_ax.plot(k_range[1:-1], accel, marker="o", color="orange")
    accel_ax.set_xlim(k_range[0], k_range[-1])
    accel_ax.axvline(x=elbow_idx, color="red", linestyle="--", label=f"k={optimal_k}")
    accel_ax.set_xlabel("# Merges")
    accel_ax.set_ylabel("Acceleration (2nd derivative)")
    accel_ax.set_xticks(xticks)
    accel_ax.set_ylim(*accel_ax_ylim)
    accel_ax.set_yticks(np.linspace(*accel_ax_ylim, 5))

    # plt.savefig(f"savefigs/{dataset}_{direction}_elbow.eps", format="eps")

    return optimal_k, fig, merge_ax, accel_ax

def plot_dendrogram(mat, link, k=None, ax=None):
    """Render linkage matrix into a dendrogram."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(20, 12))
    else:
        fig = ax.get_figure()

    cutoff = "default"
    if k is not None:
        if k < 1 or k > len(link):
            raise ValueError("k is out of range.")
        cutoff = (link[-(k - 1), 2] + link[-k, 2]) / 2 # Make a cutoff at a specified number of clusters (k).
        
    # Plot dendrogram.
    dendro = dendrogram(
        link,
        labels=c.get_labels(mat),
        ax=ax,
        leaf_rotation=90,
        color_threshold=cutoff,
        above_threshold_color="black",
    )

    if cutoff != "default":
        ax.axhline(y=cutoff, c="red", linestyle="--", linewidth=1.5,
                        label=f"Elbow method cutoff  = {cutoff:.3f} (k={k})")
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=9)
    ax.set_ylabel("Cosine Distance")
    ax.legend(loc="upper right")
    # plt.savefig(f"savefigs/{dataset}_{direction}.eps", format="eps")

    return fig, ax

def plot_diagnostics(mat, link):
    fig = plt.figure(figsize=(28, 12))
    
    dendro_ax = fig.add_subplot(1, 3, (1, 2))  # Takes up 2/3 of width.
    merge_ax = fig.add_subplot(3, 3, 3)
    accel_ax = fig.add_subplot(3, 3, 6)

    optimal_k, *_ = plot_elbow(link, merge_ax, accel_ax)
    plot_dendrogram(mat, link, optimal_k, dendro_ax)

    return fig
import pandas as pd

# Code used to transform linkage matrix into a more readable format.

def get_short_labels(mat):
    """Labels for each cell to eventually be used on the heatmap axes."""
    indices = mat.index
    labels = []
    for root_id, type_, side in indices:
        labels.append(f"{root_id} ({type_})")
    return labels

def linkage_to_readable(link, labels):
    """
    Convert a linkage matrix to a human-readable DataFrame.
    `labels` is a list of original leaf label strings.
    """
    n = len(labels)
    # scipy linkage: new cluster ID for merge i is n + i
    clusters = {i: [labels[i]] for i in range(n)}

    rows = []
    for i, (c1, c2, dist, size) in enumerate(link):
        c1, c2 = int(c1), int(c2)
        new_id = n + i
        merged = clusters[c1] + clusters[c2]
        clusters[new_id] = merged
        rows.append({
            "merge_step": i + 1,
            "cluster_1_members": clusters[c1],
            "cluster_2_members": clusters[c2],
            "merged_members": merged,
            "cosine_distance": dist,
            "merged_cluster_size": int(size),
        })

    return pd.DataFrame(rows)
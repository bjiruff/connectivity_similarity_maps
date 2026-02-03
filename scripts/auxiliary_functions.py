
from typing import List
from collections import namedtuple
import pandas as pd
from .data_loader import DATASETS

def get_label(id_: List):
    """Labels for each cell to eventually be used on the heatmap axes."""
    # id[0] = root id.
    # id[1] = cell type.
    # id[2] = side.
    return f"{id_[0]} / {id_[1]}({id_[2]})"


def get_connectivity_matrix(cell_types: List, dataset: str):
    """Returns a DataFrame describing the upstream and downstream connections to and from a given list of cell types."""

    if dataset not in ["fafb", "mcns", "manc"]:
        raise ValueError("Invalid dataset.")

    celltypes_df = DATASETS[dataset].celltypes_df
    classifications_df = DATASETS[dataset].classifications_df
    connections_df = DATASETS[dataset].connections_df

    PartnerData = namedtuple("PartnerData",
                             ["target_id", "target_type", "target_side", "partner_id", "direction", "syn_count",
                              "partner_type"])

    rows = []
    ids = []
    id_to_type = {}
    id_to_side = {}

    for type_ in cell_types:
        type_ids = celltypes_df[celltypes_df["primary_type"] == type_]["root_id"].values
        if type_ids.size == 0:
            raise ValueError(f"Type {type_} does not exist in the dataset.")
        for id_ in type_ids:
            side = classifications_df[classifications_df["root_id"] == id_]["side"].iloc[0]
            id_to_side[id_] = side
            id_to_type[id_] = type_
            # Get upstream connections.
            upstream_df = connections_df[connections_df["post_root_id"] == id_]
            for tup in upstream_df.itertuples():
                type_df = celltypes_df[celltypes_df["root_id"] == tup.pre_root_id]["primary_type"]
                if not type_df.empty:
                    upstream_type = type_df.iloc[0]
                else:
                    continue
                upstream_connection = PartnerData(
                    target_id=id_,
                    target_type=type_,
                    target_side=side,
                    partner_id=tup.pre_root_id,
                    direction="upstream",
                    syn_count=tup.syn_count,
                    partner_type=upstream_type
                )
                rows.append(upstream_connection)
            # Get downstream connections.
            downstream_df = connections_df[connections_df["pre_root_id"] == id_]
            for tup in downstream_df.itertuples():
                type_df = celltypes_df[celltypes_df["root_id"] == tup.post_root_id]["primary_type"]
                if not type_df.empty:
                    downstream_type = type_df.iloc[0]
                else:
                    continue
                downstream_connection = PartnerData(
                    target_id=id_,
                    target_type=type_,
                    target_side=side,
                    partner_id=tup.post_root_id,
                    direction="downstream",
                    syn_count=tup.syn_count,
                    partner_type=downstream_type
                )
                rows.append(downstream_connection)

        # Record soma side names for different datasets.
        dataset_side_names = {}
        if dataset == "fafb" or dataset == "mcns":
            dataset_side_names["left"] = "left"
            dataset_side_names["right"] = "right"
            # dataset_side_names["center"] = "center"
        elif dataset == "manc":
            dataset_side_names["left"] = "LHS"
            dataset_side_names["right"] = "RHS"

        # Ensure type ids are ordered according to soma sides left, right, and center.
        left_ids, right_ids, other_ids = [], [], []

        for id_ in type_ids:
            side = id_to_side[id_]
            if side == dataset_side_names["left"]:
                left_ids.append(id_)
            elif side == dataset_side_names["right"]:
                right_ids.append(id_)
            else:
                other_ids.append(id_)

        ids.extend(left_ids + right_ids + other_ids)

    partner_df = pd.DataFrame(rows)

    agg = (
        partner_df
        .groupby(["target_id", "target_type", "target_side", "partner_type", "direction"])["syn_count"]
        .sum()
        .reset_index()
    )

    mat = agg.pivot_table(
        index=["target_id", "target_type", "target_side"],
        columns=["direction", "partner_type"],
        values="syn_count",
        fill_value=0
    )

    # Reordering certain ids in the heatmap. Uncomment to get the specific ordering used in the paper.
    # if dataset == "fafb":
    #     if 720575940627790991 in ids and 720575940611108676 in ids:
    #         ind_1 = ids.index(720575940627790991)
    #         ind_2 = ids.index(720575940611108676)
    #         ids[ind_1] = 720575940611108676
    #         ids[ind_2] = 720575940627790991

    #     if 720575940613635737 in ids and 720575940615160239 in ids:
    #         ind_1 = ids.index(720575940613635737)
    #         ind_2 = ids.index(720575940615160239)
    #         ids[ind_1] = 720575940615160239
    #         ids[ind_2] = 720575940613635737

    # Reorder matrix so that the neurons are ordered by cell type, as ids is built in order of the types in cell_type.
    mat = mat.loc[ids]

    return mat
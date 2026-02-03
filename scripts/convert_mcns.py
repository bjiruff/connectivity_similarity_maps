import pandas as pd
from .paths import RAW_DIR, PROCESSED_DIR

# Converting MCNS to FAFB-like sheets.

def main():
    # Downloaded from https://male-cns.janelia.org/download/#__tabbed_3_3
    raw_annotations_df = pd.read_feather(RAW_DIR / "body-annotations-male-cns-v0.9-minconf-0.5.feather")
    raw_connections_df = pd.read_feather(RAW_DIR / "connectome-weights-male-cns-v0.9-minconf-0.5.feather")
    # raw_neurotransmitter_df = pd.read_feather(RAW_DIR / "body-neurotransmitters-male-cns-v0.9.feather")

    # Make cell types csv.
    celltypes_df = raw_annotations_df[["bodyId", "type"]]
    celltypes_df = celltypes_df.rename(columns={"bodyId": "root_id", "type": "primary_type"})
    celltypes_df = celltypes_df[celltypes_df["primary_type"].notna()]
    celltypes_df.to_csv(PROCESSED_DIR / "mcns_celltypes.csv", index=False)
    print("mcns_celltypes.csv created")

    # Make classifications csv.
    classifications_df = raw_annotations_df[["bodyId", "superclass", "class", "subclass", "itoleeHl", "somaSide"]]
    classifications_df = classifications_df.rename(columns={
        "bodyId": "root_id",
        "superclass": "super_class",
        "subclass": "sub_class",
        "itoleeHl": "hemilineage",
        "somaSide": "side"
        })
    classifications_df["side"] = (
        classifications_df["side"]
        .replace({
            "L": "left",
            "R": "right",
            "M": "center"
        })
    )
    classifications_df.to_csv(PROCESSED_DIR / "mcns_classifications.csv", index=False)
    print("mcns_classifications.csv created")

    # # Make neurotransmitters csv.
    # neurotransmitter_df = raw_neurotransmitter_df[[
    #     "body", 
    #     "predicted_nt", 
    #     "predicted_nt_confidence", 
    #     "cell_type",
    #     "celltype_predicted_nt",
    #     "celltype_predicted_nt_confidence",
    #     "consensus_nt"
    #     ]]
    # neurotransmitter_df = neurotransmitter_df.rename(columns={
    #     "body": "root_id",
    #     "predicted_nt": "nt_type",
    #     "predicted_nt_confidence": "nt_type_score",
    #     "celltype_predicted_nt": "celltype_nt_type",
    #     "celltype_predicted_nt_confidence": "celltype_nt_type_score",
    # })
    # neurotransmitter_df[["nt_type", "cell_type", "consensus_nt"]] = (
    #     neurotransmitter_df[["nt_type", "cell_type", "consensus_nt"]]
    #     .replace({
    #         "acetylcholine": "ACH",
    #         "dopamine": "DA",
    #         "gaba": "GABA",
    #         "glutamate": "GLUT",
    #         "histamine": "HIST",
    #         "octopamine": "OCT",
    #         "serotonin": "SER",
    #         "unclear": pd.NA 
    #     })
    # )
    # neurotransmitter_df.to_csv(PROCESSED_DIR / "mcns_neurotransmitters.csv", index=False)
    # print("mcns_neurotransmitters.csv created")

    # Make connections csv.
    # Make separate csvs for all traced connections and all traced connections with synapse count > 5.
    raw_connections_df = raw_connections_df[raw_connections_df["weight"] >= 5]
    header = [
        "pre_root_id",
        "post_root_id",
        "syn_count"
    ]
    data = []
    for row in raw_connections_df.itertuples():
        body_pre = row.body_pre
        body_post = row.body_post
        weight = row.weight
        body_pre_df = raw_annotations_df[raw_annotations_df["bodyId"] == body_pre]
        body_post_df = raw_annotations_df[raw_annotations_df["bodyId"] == body_post]
        if body_pre_df.empty or body_post_df.empty:
            continue
        if body_pre_df["status"].iloc[0] != "Traced" or body_post_df["status"].iloc[0] != "Traced":
            continue
        data.append([body_pre, body_post, weight])
    connections_df = pd.DataFrame(data=data, columns=header)
    connections_df.to_csv(PROCESSED_DIR / "mcns_connections.csv", index=False)
    print("mcns_connections.csv created")

if __name__ == "__main__":
    main()


import pandas as pd
import neuprint
from neuprint import Client
from .paths import PROCESSED_DIR

# Converting MANC to FAFB-like sheets
def main():
    TOKEN = "YOUR_TOKEN_HERE"
    c = Client("neuprint.janelia.org", dataset="manc:v1.2.1", token=TOKEN)

    raw_neurons_df, _ = neuprint.queries.fetch_neurons(returned_columns=[
        "bodyId",
        "type",
        "hemilineage",
        "predictedNt",
        "predictedNtProb",
        "class",
        "subclass",
        "rootSide",
        "celltypePredictedNt",
    ])

    # Create cell types, neurotransmitter, and classifications csvs.
    celltypes_df = raw_neurons_df[["bodyId", "type"]]
    # neurotransmitter_df = raw_neurons_df[["bodyId", "predictedNt", "predictedNtProb", "type", "celltypePredictedNt"]]
    classifications_df = raw_neurons_df[["bodyId", "class", "subclass", "hemilineage", "rootSide"]]

    celltypes_df = celltypes_df.rename(columns={"bodyId": "root_id", "type": "primary_type"})
    celltypes_df = celltypes_df[celltypes_df["primary_type"].notna()]
    classifications_df = classifications_df.rename(columns={
        "bodyId": "root_id",
        "subclass": "sub_class",
        "rootSide": "side"
    })
    # neurotransmitter_df = neurotransmitter_df.rename(columns={
    #     "bodyId": "root_id",
    #     "predictedNt": "nt_type",
    #     "predictedNtProb": "nt_type_score",
    #     "type": "cell_type",
    #     "celltypePredictedNt": "celltype_nt_type"
    # })
    # neurotransmitter_df[["nt_type", "celltype_nt_type"]] = (
    #     neurotransmitter_df[["nt_type", "celltype_nt_type"]]
    #     .replace({
    #         "acetylcholine": "ACH",
    #         "glutamate": "GLUT",
    #         "gaba": "GABA",
    #         "dopamine": "DA",
    #         "serotonin": "SER",
    #         "octopamine": "OCT"
    #     })
    # )

    celltypes_df.to_csv(PROCESSED_DIR / "manc_celltypes.csv", index=False)
    print("manc_celltypes.csv created")
    classifications_df.to_csv(PROCESSED_DIR / "manc_classifications.csv", index=False)
    print("manc_classifications.csv created")
    # neurotransmitter_df.to_csv(PROCESSED_DIR / "manc_neurotransmitters.csv", index=False)
    # print("manc_neurotransmitters.csv created")

    _, raw_connections_df = neuprint.queries.fetch_adjacencies()

    # Make connections csv.
    rename_mapping = {
        "bodyId_pre": "pre_root_id",
        "bodyId_post": "post_root_id",
        "weight": "syn_count"
    }
    connections_df = raw_connections_df.rename(columns=rename_mapping)
    connections_df = connections_df.groupby(["pre_root_id", "post_root_id"], as_index=False)["syn_count"].sum()
    connections_df = connections_df[connections_df["syn_count"] >= 5]
    connections_df.to_csv(PROCESSED_DIR / "manc_connections.csv", index=False)
    print("manc_connections.csv created")

if __name__ == "__main__":
    main()
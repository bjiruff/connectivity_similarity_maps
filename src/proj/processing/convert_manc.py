import pandas as pd
import neuprint
from neuprint import Client
from proj.config.paths import PROCESSED_DIR
from proj.config.secret import NEUPRINT_KEY

# Converting MANC to FAFB-like sheets
def main():
    TOKEN = NEUPRINT_KEY
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
    classifications_df = raw_neurons_df[["bodyId", "class", "subclass", "hemilineage", "rootSide"]]

    celltypes_df = celltypes_df.rename(columns={"bodyId": "root_id", "type": "primary_type"})
    celltypes_df = celltypes_df[celltypes_df["primary_type"].notna()]
    # Some cell types have commas to denote that the neuron is assigned to more than one cell. We only want the primary type.
    celltypes_df["primary_type"] = celltypes_df["primary_type"].apply(lambda x: x.split(",")[0])
    classifications_df = classifications_df.rename(columns={
        "bodyId": "root_id",
        "subclass": "sub_class",
        "rootSide": "side"
    })

    celltypes_df.to_csv(PROCESSED_DIR / "manc_celltypes.csv", index=False)
    print("manc_celltypes.csv created")
    classifications_df.to_csv(PROCESSED_DIR / "manc_classifications.csv", index=False)
    print("manc_classifications.csv created")

    _, raw_cell_connections_df = neuprint.queries.fetch_adjacencies()

    # Make connections csv.
    rename_mapping = {
        "bodyId_pre": "pre_root_id",
        "bodyId_post": "post_root_id",
        "weight": "syn_count"
    }
    cell_connections_df = raw_cell_connections_df.rename(columns=rename_mapping)
    cell_connections_df = cell_connections_df.groupby(["pre_root_id", "post_root_id"], as_index=False)["syn_count"].sum()
    cell_connections_df = cell_connections_df[cell_connections_df["syn_count"] >= 5]
    cell_connections_df.to_csv(PROCESSED_DIR / "manc_cell_connections.csv", index=False)
    print("manc_cell_connections.csv created")

    id_to_type = celltypes_df.set_index("root_id")["primary_type"]
    type_connections_df = cell_connections_df.copy().rename(columns={"pre_root_id": "pre_type", "post_root_id": "post_type"})
    type_connections_df["pre_type"] = type_connections_df["pre_type"].map(id_to_type)
    type_connections_df["post_type"] = type_connections_df["post_type"].map(id_to_type)
    type_connections_df = type_connections_df.groupby(["pre_type", "post_type"], as_index=False)["syn_count"].sum()
    type_connections_df.to_csv(PROCESSED_DIR / "manc_type_connections.csv", index=False)
    print("manc_type_connections.csv created")

if __name__ == "__main__":
    main()
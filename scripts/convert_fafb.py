import shutil
import pandas as pd
from .paths import RAW_DIR, PROCESSED_DIR

# Renaming FAFB sheets and doing minor processing on connections data.

# Download consolidated_cell_types.csv, classification.csv, neurons.csv, connections_princeton.csv from https://codex.flywire.ai/api/download?dataset=fafb
def main():
    shutil.copy(RAW_DIR / "consolidated_cell_types.csv", PROCESSED_DIR / "fafb_celltypes.csv")
    print("fafb_celltypes.csv created")
    shutil.copy(RAW_DIR / "classification.csv", PROCESSED_DIR / "fafb_classifications.csv")
    print("fafb_classifications.csv created")
    # shutil.copy(RAW_DIR / "neurons.csv", PROCESSED_DIR / "fafb_neurotransmitters.csv")
    # print("fafb_neurotransmitters.csv created")

    raw_connections_df = pd.read_csv(RAW_DIR / "connections_princeton.csv")
    connections_df = raw_connections_df.groupby(["pre_root_id", "post_root_id"], as_index=False)["syn_count"].sum()
    connections_df.to_csv(PROCESSED_DIR / "fafb_connections.csv", index=False)
    print("fafb_connections.csv created")

if __name__ == "__main__":
    main()

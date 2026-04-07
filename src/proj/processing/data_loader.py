import pandas as pd
from proj.config.paths import PROCESSED_DIR

connectomes = ["fafb", "mcns", "manc"]

class Dataset:
    def __init__(self, cell_connections_df, type_connections_df, celltypes_df, classifications_df):
        self.cell_connections_df = cell_connections_df
        self.type_connections_df = type_connections_df
        self.celltypes_df = celltypes_df
        self.classifications_df = classifications_df

missing = []
for c in connectomes:
    required_files = [
        f"{c}_cell_connections.csv",
        f"{c}_type_connections.csv",
        f"{c}_celltypes.csv",
        f"{c}_classifications.csv",
    ]
    missing.extend([f for f in required_files if not (PROCESSED_DIR / f).is_file()])
    
if missing:
    missing_list = "\n  ".join(missing)
    raise FileNotFoundError(
        f"{str(PROCESSED_DIR)} has missing files:\n  {missing_list}\nPlease run convert_datasets.py to generate necessary files."
    )

DATASETS = {}
for c in connectomes:
    DATASETS[c] = Dataset(
        pd.read_csv(PROCESSED_DIR / f"{c}_cell_connections.csv"),
        pd.read_csv(PROCESSED_DIR / f"{c}_type_connections.csv"),
        pd.read_csv(PROCESSED_DIR / f"{c}_celltypes.csv"),
        pd.read_csv(PROCESSED_DIR / f"{c}_classifications.csv"),
    )

OA_MAP_DF = pd.read_csv(PROCESSED_DIR / "oa_name_map.csv")
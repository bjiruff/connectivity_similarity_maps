import pandas as pd
from .paths import PROCESSED_DIR

class Dataset:
    def __init__(self, connections_df, celltypes_df, classifications_df):
        self.connections_df = connections_df
        self.celltypes_df = celltypes_df
        self.classifications_df = classifications_df

DATASETS = {
    "fafb": Dataset(
        pd.read_csv(PROCESSED_DIR / "fafb_connections.csv"),
        pd.read_csv(PROCESSED_DIR / "fafb_celltypes.csv"),
        pd.read_csv(PROCESSED_DIR / "fafb_classifications.csv"),
    ),
    "mcns": Dataset(
        pd.read_csv(PROCESSED_DIR / "mcns_connections.csv"),
        pd.read_csv(PROCESSED_DIR / "mcns_celltypes.csv"),
        pd.read_csv(PROCESSED_DIR / "mcns_classifications.csv"),
    ),
    "manc": Dataset(
        pd.read_csv(PROCESSED_DIR / "manc_connections.csv"),
        pd.read_csv(PROCESSED_DIR / "manc_celltypes.csv"),
        pd.read_csv(PROCESSED_DIR / "manc_classifications.csv"),
    ),
}
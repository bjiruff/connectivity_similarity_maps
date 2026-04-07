from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent
ROOT = CONFIG_DIR.parents[2]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SAVEFIGS_DIR = ROOT / "savefigs"
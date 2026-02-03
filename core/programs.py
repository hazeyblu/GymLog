# core/programs.py

import pandas as pd
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROGRAMS_DIR = PROJECT_ROOT / "programs"

def load_program_meta(program_name: str) -> dict:
    meta_file = PROGRAMS_DIR / program_name / "meta.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"meta.json not found for {program_name}")
    with open(meta_file, "r") as f:
        return json.load(f)

def load_day(program_name: str, day_id: int) -> pd.DataFrame:
    day_file = PROGRAMS_DIR / program_name / f"day_{day_id}.feather"
    if not day_file.exists():
        raise FileNotFoundError(f"Workout file missing: day_{day_id}.feather")
    return pd.read_feather(day_file).sort_values("order")

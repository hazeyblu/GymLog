# core/io.py

from pathlib import Path
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = PROJECT_ROOT / "logs"
BODY_METRICS_SUFFIX = "_body.feather"

def append_workout_logs(username: str, rows: list[dict]) -> None:
    if not rows:
        return

    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"{username}.feather"

    df_new = pd.DataFrame(rows)

    if log_file.exists():
        df_existing = pd.read_feather(log_file)
        df_all = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_feather(log_file)

def load_user_logs(username: str) -> pd.DataFrame:
    log_file = LOGS_DIR / f"{username}.feather"
    if not log_file.exists():
        return pd.DataFrame()
    return pd.read_feather(log_file)

def delete_workout_by_id(username: str, workout_id: str) -> int:
    if not workout_id:
        return 0

    log_file = LOGS_DIR / f"{username}.feather"
    if not log_file.exists():
        return 0

    df = pd.read_feather(log_file)
    if "workout_id" not in df.columns:
        return 0

    before = len(df)
    df = df[df["workout_id"] != workout_id]
    after = len(df)

    df.to_feather(log_file)
    return before - after

def append_body_metrics(username: str, rows: list[dict]) -> None:
    if not rows:
        return

    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"{username}{BODY_METRICS_SUFFIX}"

    df_new = pd.DataFrame(rows)

    if log_file.exists():
        df_existing = pd.read_feather(log_file)
        df_all = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_feather(log_file)

def load_body_metrics(username: str) -> pd.DataFrame:
    log_file = LOGS_DIR / f"{username}{BODY_METRICS_SUFFIX}"
    if not log_file.exists():
        return pd.DataFrame()
    return pd.read_feather(log_file)

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

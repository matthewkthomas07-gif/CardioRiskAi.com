"""Download, clean, and merge multiple UCI heart-disease databases."""

from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
RAW_SOURCES = {
    "Cleveland Clinic": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
    "Hungarian Institute": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.hungarian.data",
    "VA Long Beach": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.va.data",
    "Switzerland": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.switzerland.data",
}

COLUMNS = [
    "Age",
    "Sex",
    "ChestPain",
    "SystolicBP",
    "Cholesterol",
    "FastingBS",
    "RestingECG",
    "MaxHR",
    "ExerciseAngina",
    "Oldpeak",
    "Slope",
    "NumVessels",
    "Thal",
    "target",
]

FEATURES = COLUMNS[:-1]


def download_raw_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    slugs = {
        "Cleveland Clinic": "cleveland",
        "Hungarian Institute": "hungarian",
        "VA Long Beach": "va",
        "Switzerland": "switzerland",
    }
    for name, url in RAW_SOURCES.items():
        path = DATA_DIR / f"raw_{slugs[name]}.data"
        if not path.exists():
            urllib.request.urlretrieve(url, path)


def _slug_from_path(path: Path) -> str:
    name = path.stem.replace("raw_", "")
    return {
        "cleveland": "Cleveland Clinic",
        "hungarian": "Hungarian Institute",
        "va": "VA Long Beach",
        "switzerland": "Switzerland",
    }.get(name, name)


def _map_thal(value: float) -> float | np.nan:
    """UCI codes 3,6,7 -> model codes 1,2,3."""
    mapping = {3.0: 1.0, 6.0: 2.0, 7.0: 3.0}
    if pd.isna(value):
        return np.nan
    v = float(value)
    return mapping.get(v, np.nan)


def _map_chest_pain(value: float) -> float | np.nan:
    """UCI angina types 1-4 -> 0-3."""
    mapping = {1.0: 0.0, 2.0: 1.0, 3.0: 2.0, 4.0: 3.0}
    if pd.isna(value):
        return np.nan
    return mapping.get(float(value), np.nan)


def _map_slope(value: float) -> float | np.nan:
    """UCI slope 1-3 -> 0-2."""
    mapping = {1.0: 0.0, 2.0: 1.0, 3.0: 2.0}
    if pd.isna(value):
        return np.nan
    return mapping.get(float(value), np.nan)


def load_single(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, names=COLUMNS, na_values="?")
    df["source"] = _slug_from_path(path)
    df["ChestPain"] = df["ChestPain"].apply(_map_chest_pain)
    df["Thal"] = df["Thal"].apply(_map_thal)
    df["Slope"] = df["Slope"].apply(_map_slope)
    df["NumVessels"] = df["NumVessels"].clip(0, 3)
    df["HeartDisease"] = (df["target"] > 0).astype(int)
    df = df.drop(columns=["target"])
    return df


def clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Keep rows with valid labels and impute missing clinical values."""
    out = df.copy()
    for col in FEATURES:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=["HeartDisease"])
    # Drop rows missing more than 4 features
    missing_per_row = out[FEATURES].isna().sum(axis=1)
    out = out[missing_per_row <= 4].copy()

    for col in FEATURES:
        if out[col].isna().any():
            out[col] = out[col].fillna(out[col].median())

    for col in FEATURES:
        lo, hi = _limits(col)
        out[col] = out[col].clip(lo, hi)

    out[FEATURES] = out[FEATURES].round().astype(int)
    out.loc[out["Oldpeak"] != out["Oldpeak"].astype(int), "Oldpeak"] = out["Oldpeak"]
    out["Oldpeak"] = out["Oldpeak"].astype(float)
    return out.reset_index(drop=True)


def _limits(col: str) -> tuple[float, float]:
    limits = {
        "Age": (1, 120),
        "Sex": (0, 1),
        "ChestPain": (0, 3),
        "SystolicBP": (80, 250),
        "Cholesterol": (100, 600),
        "FastingBS": (0, 1),
        "RestingECG": (0, 2),
        "MaxHR": (60, 220),
        "ExerciseAngina": (0, 1),
        "Oldpeak": (0.0, 10.0),
        "Slope": (0, 2),
        "NumVessels": (0, 3),
        "Thal": (1, 3),
    }
    return limits[col]


def build_combined_dataset(download: bool = True) -> pd.DataFrame:
    if download:
        download_raw_files()

    frames = []
    for path in sorted(DATA_DIR.glob("raw_*.data")):
        frames.append(clean_frame(load_single(path)))

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=FEATURES + ["HeartDisease"])
    return combined


def save_heart_csv(df: pd.DataFrame | None = None) -> Path:
    if df is None:
        df = build_combined_dataset()
    out_path = DATA_DIR / "heart.csv"
    export = df[FEATURES + ["HeartDisease"]].copy()
    export.to_csv(out_path, index=False)
    return out_path

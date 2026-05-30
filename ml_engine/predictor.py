import os
import json
import logging
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================
# CLOUD PATH RESOLUTION
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "models" / "final_multimodal_dataset.parquet"
ARTIFACT_DIR = BASE_DIR / "models" / "artifacts"
CHECKPOINT_PATH = BASE_DIR / "models" / "multi_horizon_lgb.pkl"
PREDICTION_OUTPUT = BASE_DIR / "models" / "predictions" / "latest_predictions.parquet"

THRESHOLD = 0.5

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def sigmoid(x):
    """Squashes regression z-scores into a 0-1 probability for the frontend."""
    return 1 / (1 + np.exp(-x))


def load_feature_columns():
    path = ARTIFACT_DIR / "feature_columns.json"
    if not path.exists():
        raise FileNotFoundError(f"Feature columns file not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        feature_cols = json.load(file)
    logger.info(f"Loaded {len(feature_cols)} feature columns.")
    return feature_cols


def load_latest_dataset():
    logger.info("Loading dataset and engineering real-time features...")
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_parquet(DATASET_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    # Sort properly so rolling calculations work
    df = df.sort_values(["Stock_symbol", "Date"]).reset_index(drop=True)

    # ============================================================
    # FEATURE ENGINEERING (Must exactly match train.py)
    # ============================================================
    grouped = df.groupby("Stock_symbol")
    df["return_1d"] = grouped["Close"].pct_change()
    df["return_3d"] = grouped["Close"].pct_change(3)
    df["return_5d"] = grouped["Close"].pct_change(5)
    df["volatility_10"] = (
        grouped["return_1d"].rolling(10).std().reset_index(0, drop=True)
    )
    df["return_5d_rank"] = df.groupby("Date")["return_5d"].rank(pct=True)

    if "VIX_level" in df.columns:
        median_vix = df["VIX_level"].median()
        df["high_vol_regime"] = (df["VIX_level"] > median_vix).astype(int)

    # ============================================================
    # EXTRACT LATEST DAY PER STOCK
    # ============================================================
    # Grab the most recent row available for EVERY stock, avoiding
    # situations where a single straggler date filters out the rest of the market.
    latest_df = (
        df.sort_values("Date").groupby("Stock_symbol", as_index=False).tail(1).copy()
    )

    logger.info(f"Loaded latest cross-section for {len(latest_df)} stocks.")
    return latest_df


# ============================================================
# MAIN PIPELINE
# ============================================================


def run_inference():
    logger.info("=" * 60)
    logger.info("RUNNING FINANCIAL INFERENCE PIPELINE (MULTI-HORIZON)")
    logger.info("=" * 60)

    # 1. Load Data & Features
    df = load_latest_dataset()
    feature_cols = load_feature_columns()

    # Ensure all required features exist in the dataframe before predicting
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        raise KeyError(
            f"Missing engineered columns required for prediction: {missing_cols}"
        )

    X = df[feature_cols].values

    # 2. Load LightGBM Model
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found: {CHECKPOINT_PATH}")

    logger.info("Loading MultiOutputRegressor Model...")
    model = joblib.load(CHECKPOINT_PATH)

    # 3. Generate Predictions (Returns 1D, 3D, 5D targets)
    logger.info("Generating predictions...")
    preds = model.predict(X)

    df["pred_1d"] = preds[:, 0]
    df["pred_3d"] = preds[:, 1]
    df["pred_5d"] = preds[:, 2]

    # 4. Bridge to Frontend Requirements
    df["mean_z_score"] = df[["pred_1d", "pred_3d", "pred_5d"]].mean(axis=1)
    df["buy_probability"] = df["mean_z_score"].apply(sigmoid)
    df["signal"] = (df["buy_probability"] >= THRESHOLD).astype(int)

    # Sort best to worst
    df = df.sort_values("buy_probability", ascending=False)

    # 5. Save Output
    PREDICTION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PREDICTION_OUTPUT, index=False)
    logger.info(f"Saved predictions to: {PREDICTION_OUTPUT}")

    # 6. Show Top Signals
    logger.info("\nTOP 10 BUY SIGNALS")
    logger.info("=" * 60)

    # Safely select the display price based on what we built upstream
    display_price = "Raw_Close" if "Raw_Close" in df.columns else "Close"

    print(
        df[
            [
                "Date",
                "Stock_symbol",
                display_price,
                "pred_1d",
                "pred_5d",
                "buy_probability",
                "signal",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    logger.info("Inference Complete")


if __name__ == "__main__":
    run_inference()

import os
import json
import random
import logging
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.multioutput import MultiOutputRegressor
from sqlalchemy import create_engine
from dotenv import load_dotenv
import mlflow

import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# 1. CONFIGURATION, MLFLOW READINESS & SETUP
# ============================================================
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
# Load .env from the root directory (one level up from ml_engine)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M")

# ------------------------------------------------------------
# CLOUD CONNECTIONS (AWS DB + GCP MLflow)
# ------------------------------------------------------------
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

GCP_EXTERNAL_IP = os.getenv("GCP_EXTERNAL_IP", "127.0.0.1")
mlflow.set_tracking_uri(f"http://{GCP_EXTERNAL_IP}:5000")
mlflow.set_experiment("Quant_Trading_LightGBM")

# ------------------------------------------------------------
# LOCAL FILE PATHS (Adapted to your new ml_engine/models/ structure)
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

CHECKPOINT_DIR = BASE_DIR / "models" / "history" / RUN_ID
ARTIFACTS_DIR = BASE_DIR / "models" / "artifacts"
LATEST_MODEL_PATH = BASE_DIR / "models" / "multi_horizon_lgb.pkl"

MAX_HORIZON = 5
MIN_STOCKS_PER_DAY = 5

MODEL_PARAMS = {
    "n_estimators": 50,
    "learning_rate": 0.03,
    "max_depth": 7,
    "num_leaves": 63,
    "min_child_samples": 30,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_alpha": 0.1,
    "reg_lambda": 0.5,
    "random_state": SEED,
    "n_jobs": -1,
}


def main():
    logger.info(f"Starting Quant Alpha Training Pipeline | RUN ID: {RUN_ID}")

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # 2. LOAD DATA FROM AWS POSTGRESQL
    # ============================================================
    logger.info("📡 Loading dataset from AWS PostgreSQL Database...")
    try:
        query = 'SELECT * FROM deployment_dataset ORDER BY "Date" ASC;'
        df = pd.read_sql(query, engine)
        logger.info(f"Success! Initial Dataset Shape: {df.shape}")
    except Exception as e:
        logger.error(f"Database connection failed. Error: {e}")
        return

    # ============================================================
    # 3. BASIC CLEANING & FEATURE ENGINEERING
    # ============================================================
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    df = df.sort_values(["Stock_symbol", "Date"]).reset_index(drop=True)
    grouped = df.groupby("Stock_symbol")

    logger.info("⚙️ Re-verifying engineered features...")
    df["return_1d"] = grouped["Close"].pct_change()
    df["return_3d"] = grouped["Close"].pct_change(3)
    df["return_5d"] = grouped["Close"].pct_change(5)
    df["volatility_10"] = (
        grouped["return_1d"].rolling(10).std().reset_index(0, drop=True)
    )
    df["return_5d_rank"] = df.groupby("Date")["return_5d"].rank(pct=True)

    if "VIX_level" in df.columns:
        df["high_vol_regime"] = (df["VIX_level"] > df["VIX_level"].median()).astype(int)

    # ============================================================
    # 4. MULTI-HORIZON TARGETS & 5-DAY EMBARGO
    # ============================================================
    logger.info("🎯 Creating Multi-Horizon targets and enforcing 5-Day Embargo...")
    df["future_return_1d"] = grouped["Close"].shift(-1) / df["Close"] - 1
    df["future_return_3d"] = grouped["Close"].shift(-3) / df["Close"] - 1
    df["future_return_5d"] = grouped["Close"].shift(-5) / df["Close"] - 1

    initial_len = len(df)
    df = df.dropna(subset=["future_return_1d", "future_return_3d", "future_return_5d"])
    logger.info(
        f"🛡️ Embargo applied: Dropped {initial_len - len(df)} rows of unresolved recent data."
    )

    valid_mask = (
        (df["future_return_1d"] >= -0.5)
        & (df["future_return_1d"] <= 1.0)
        & (df["future_return_5d"] >= -0.5)
        & (df["future_return_5d"] <= 1.0)
    )
    df = df[valid_mask].reset_index(drop=True)

    daily_counts = df.groupby("Date")["Stock_symbol"].nunique()
    valid_dates = daily_counts[daily_counts >= MIN_STOCKS_PER_DAY].index
    df = df[df["Date"].isin(valid_dates)].reset_index(drop=True)

    logger.info("⚖️ Applying Cross-Sectional Z-Score Neutralization...")
    for horizon in [1, 3, 5]:
        target_col = f"future_return_{horizon}d"
        z_col = f"target_{horizon}d"
        df[z_col] = df.groupby("Date")[target_col].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-8)
        )

    df = df.dropna(subset=["target_1d", "target_3d", "target_5d"]).reset_index(
        drop=True
    )

    # ============================================================
    # 5. STRICT TEMPORAL SPLIT
    # ============================================================
    logger.info(
        "📅 Enforcing chronological train/val/test split (No look-ahead bias)..."
    )
    unique_dates = sorted(df["Date"].unique())
    train_end_idx = int(len(unique_dates) * 0.70)
    val_end_idx = int(len(unique_dates) * 0.85)

    train_dates = unique_dates[:train_end_idx]
    val_dates = unique_dates[train_end_idx + MAX_HORIZON : val_end_idx]
    test_dates = unique_dates[val_end_idx + MAX_HORIZON :]

    train_df = df[df["Date"].isin(train_dates)].copy()
    val_df = df[df["Date"].isin(val_dates)].copy()
    test_df = df[df["Date"].isin(test_dates)].copy()

    logger.info(
        f"Train: {train_df.shape[0]} rows | Val: {val_df.shape[0]} rows | Test: {test_df.shape[0]} rows"
    )

    # ============================================================
    # 6. DYNAMIC FEATURE SELECTION
    # ============================================================
    ignore_cols = [
        "Date",
        "Stock_symbol",
        "target_1d",
        "target_3d",
        "target_5d",
        "future_return_1d",
        "future_return_3d",
        "future_return_5d",
    ]
    sneaky_leaks = [
        c for c in df.columns if "future" in c.lower() or "target" in c.lower()
    ]
    for leak in sneaky_leaks:
        if leak not in ignore_cols:
            ignore_cols.append(leak)

    FEATURES = [
        c
        for c in train_df.columns
        if c not in ignore_cols and pd.api.types.is_numeric_dtype(train_df[c])
    ]

    feature_path = ARTIFACTS_DIR / "feature_columns.json"
    with open(feature_path, "w") as f:
        json.dump(FEATURES, f)
    logger.info(f"Locked {len(FEATURES)} dynamically extracted features for inference.")

    X_train, y_train = (
        train_df[FEATURES],
        train_df[["target_1d", "target_3d", "target_5d"]],
    )
    X_test, y_test = test_df[FEATURES], test_df[["target_1d", "target_3d", "target_5d"]]

    # ============================================================
    # 7. MODEL TRAINING (INCREMENTAL LEARNING) WITH MLFLOW
    # ============================================================
    with mlflow.start_run(run_name=f"LGBM_MultiHorizon_{RUN_ID}"):
        mlflow.log_params(MODEL_PARAMS)

        logger.info("🧠 Incrementally updating Multi-Horizon LightGBM Model...")
        if LATEST_MODEL_PATH.exists():
            logger.info(
                f"🔄 Found existing checkpoint at {LATEST_MODEL_PATH}. Appending new trees..."
            )
            old_multi_model = joblib.load(LATEST_MODEL_PATH)
            updated_estimators = []
            target_cols = ["target_1d", "target_3d", "target_5d"]

            for i, target in enumerate(target_cols):
                old_booster = old_multi_model.estimators_[i]
                new_estimator = lgb.LGBMRegressor(**MODEL_PARAMS)
                new_estimator.fit(
                    X_train, y_train[target], init_model=old_booster.booster_
                )
                updated_estimators.append(new_estimator)

            multi_model = MultiOutputRegressor(updated_estimators[0])
            multi_model.estimators_ = updated_estimators
        else:
            logger.warning("⚠️ No previous checkpoint found. Training from scratch!")
            full_params = MODEL_PARAMS.copy()
            full_params["n_estimators"] = 400
            base_model = lgb.LGBMRegressor(**full_params)
            multi_model = MultiOutputRegressor(base_model)
            multi_model.fit(X_train, y_train)

        joblib.dump(multi_model, CHECKPOINT_DIR / "multi_horizon_lgb.pkl")
        joblib.dump(multi_model, LATEST_MODEL_PATH)

        # ============================================================
        # 8. OUT-OF-SAMPLE EVALUATION
        # ============================================================
        logger.info("📊 Running Out-Of-Sample Evaluation Metrics...")
        predictions = multi_model.predict(X_test)
        test_df["pred_1d"] = predictions[:, 0]
        test_df["pred_3d"] = predictions[:, 1]
        test_df["pred_5d"] = predictions[:, 2]

        horizons = [1, 3, 5]
        daily_ic_dict, spread_dict, metrics_report = {}, {}, {}

        for horizon in horizons:
            target_col, pred_col, raw_col = (
                f"target_{horizon}d",
                f"pred_{horizon}d",
                f"future_return_{horizon}d",
            )

            rmse = np.sqrt(mean_squared_error(test_df[target_col], test_df[pred_col]))
            test_ic, _ = spearmanr(test_df[target_col], test_df[pred_col])

            daily_ic = (
                test_df.groupby("Date")
                .apply(
                    lambda x: (
                        spearmanr(x[target_col], x[pred_col])[0]
                        if len(x) > 1
                        else np.nan
                    )
                )
                .dropna()
            )
            daily_ic_dict[horizon] = daily_ic

            def calc_spread(daily_data, p_col, r_col, fraction=0.20):
                if len(daily_data) < 5:
                    return np.nan
                daily_data = daily_data.sort_values(p_col, ascending=False)
                k = max(1, int(len(daily_data) * fraction))
                return (
                    daily_data.head(k)[r_col].mean() - daily_data.tail(k)[r_col].mean()
                )

            daily_spreads = (
                test_df.groupby("Date")
                .apply(lambda x: calc_spread(x, pred_col, raw_col))
                .dropna()
            )
            spread_dict[horizon] = daily_spreads

            # Log metrics to MLflow
            mlflow.log_metric(f"RMSE_{horizon}d", rmse)
            mlflow.log_metric(f"Rank_IC_{horizon}d", test_ic)
            mlflow.log_metric(f"Mean_Spread_{horizon}d", daily_spreads.mean())

            logger.info(
                f"Horizon {horizon}D -> RMSE: {rmse:.4f} | Mean Rank IC: {daily_ic.mean():.4f} | L/S Spread: {daily_spreads.mean():.4f}"
            )

        # ============================================================
        # 9. AUTOMATED VISUALIZATION & MLFLOW UPLOAD
        # ============================================================
        logger.info("📈 Generating evaluation plots...")
        fig = plt.figure(figsize=(20, 14))

        ax1 = plt.subplot(2, 2, 1)
        ax1.bar(
            [f"{h}-Day" for h in horizons],
            [daily_ic_dict[h].mean() for h in horizons],
            color=["#1f77b4", "#ff7f0e", "#2ca02c"],
        )
        ax1.set_title("Mean Daily Rank IC by Horizon", fontsize=14, fontweight="bold")

        ax2 = plt.subplot(2, 2, 2)
        for horizon in horizons:
            rolling_ic = daily_ic_dict[horizon].rolling(window=30, min_periods=5).mean()
            ax2.plot(
                rolling_ic.index,
                rolling_ic,
                label=f"{horizon}-Day Horizon",
                linewidth=2,
            )
        ax2.set_title("30-Day Rolling Mean Rank IC", fontsize=14, fontweight="bold")
        ax2.legend()

        plt.tight_layout()
        eval_plot_path = CHECKPOINT_DIR / "evaluation_metrics.png"
        plt.savefig(eval_plot_path)
        plt.close()

        # Send plots and feature columns list directly to MLflow UI
        mlflow.log_artifact(str(eval_plot_path))
        mlflow.log_artifact(str(feature_path))

        logger.info("🟢 Training pipeline completed and versioned successfully.")


if __name__ == "__main__":
    main()

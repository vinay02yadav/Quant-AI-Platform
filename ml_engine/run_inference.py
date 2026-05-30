import os
import pandas as pd
from sqlalchemy import create_engine
import joblib
import json
from pathlib import Path
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
# Load .env from the root directory
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# WIRED TO CLOUD AWS RDS
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# Dynamically resolve to the new ml_engine/models/ structure
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "multi_horizon_lgb.pkl"
FEATURES_PATH = BASE_DIR / "models" / "artifacts" / "feature_columns.json"


def run_inference():
    print("📡 Fetching recent market data for rolling feature calculations...")

    # Pull the last 30 days of data so we can calculate 10-day rolling metrics
    query = """
        SELECT * FROM deployment_dataset 
        WHERE "Date" >= (SELECT MAX("Date") - INTERVAL '30 days' FROM deployment_dataset)
        ORDER BY "Date" ASC
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        print("❌ No data found in deployment_dataset. Did feature_engineer.py run?")
        return

    # 1. RECREATE THE TRANSIENT FEATURES (Requires Historical Rows)
    grouped = df.groupby("Stock_symbol")
    df["return_1d"] = grouped["Close"].pct_change()
    df["return_5d"] = grouped["Close"].pct_change(5)
    df["volatility_10"] = grouped["return_1d"].transform(lambda x: x.rolling(10).std())
    df["return_5d_rank"] = df.groupby("Date")["return_5d"].rank(pct=True)

    if "VIX_level" in df.columns:
        df["high_vol_regime"] = (df["VIX_level"] > df["VIX_level"].median()).astype(int)
    else:
        df["high_vol_regime"] = 0

    df = df.fillna(0)

    # 2. ISOLATE TODAY'S ROW FOR PREDICTION
    latest_date = df["Date"].max()
    df_live = df[df["Date"] == latest_date].copy()

    print(f"✅ Extracted {len(df_live)} live tickers for Target Date: {latest_date}")

    # 3. Load Model & Features
    try:
        model = joblib.load(MODEL_PATH)
        with open(FEATURES_PATH, "r") as f:
            features = json.load(f)
        print("✅ LightGBM Model & Feature schemas loaded.")
    except Exception as e:
        print(f"❌ Failed to load model or feature JSON: {e}")
        return

    # 4. Predict
    print("🧠 Running quantitative predictions...")
    X_live = df_live[features]
    predictions = model.predict(X_live)

    # 5. Format results
    df_live["Pred_1D"] = predictions[:, 0]
    df_live["Pred_3D"] = predictions[:, 1]
    df_live["Pred_5D"] = predictions[:, 2]

    results = df_live[
        ["Date", "Stock_symbol", "Close", "Pred_1D", "Pred_3D", "Pred_5D"]
    ]

    # 6. Save to Database
    results.to_sql("daily_signals", con=engine, if_exists="replace", index=False)
    print(
        "🟢 SUCCESS! AI Trading signals generated and saved to 'daily_signals' table."
    )


if __name__ == "__main__":
    run_inference()

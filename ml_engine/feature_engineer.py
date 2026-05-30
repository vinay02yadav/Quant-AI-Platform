import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

# 🔌 WIRED TO AWS RDS via .env
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# THE EXACT 86 COLUMNS YOUR MODEL EXPECTS
EXPECTED_COLUMNS = [
    "Date",
    "Stock_symbol",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "RSI",
    "MACD",
    "MACD_SIGNAL",
    "SMA_20",
    "SMA_50",
    "VOLATILITY_20",
    "daily_news_chunk",
    "news_count",
    "qwen_market_summary",
    "sentiment_label",
    "sentiment_score",
    "sentiment_numeric",
    "SPY_return_1d",
    "SPY_return_5d",
    "SPY_volatility",
    "QQQ_return_1d",
    "QQQ_return_5d",
    "QQQ_volatility",
    "VIX_level",
    "VIX_change_1d",
    "VIX_return_5d",
    "DXY_return_1d",
    "TNX_change_1d",
    "OIL_return_1d",
    "XLK_return_1d",
    "XLK_return_5d",
    "XLF_return_1d",
    "XLF_return_5d",
    "XLE_return_1d",
    "XLE_return_5d",
    "XLV_return_1d",
    "XLV_return_5d",
    "no_news_flag",
    "days_since_news",
    "earnings_cycle_day",
    "days_to_earnings",
    "earnings_window",
    "market_sentiment",
    "market_news_count",
    "last_sentiment",
    "sentiment_decay",
    "propagated_sentiment",
    "sentiment_3d_avg",
    "sentiment_7d_avg",
    "sentiment_14d_avg",
    "sentiment_volatility_7d",
    "news_count_3d",
    "news_count_7d",
    "no_news_ratio_7d",
    "daily_return",
    "return_3d",
    "return_7d",
    "close_mean_3",
    "close_std_3",
    "volume_mean_3",
    "close_mean_5",
    "close_std_5",
    "volume_mean_5",
    "close_mean_10",
    "close_std_10",
    "volume_mean_10",
    "return_lag_1",
    "sentiment_lag_1",
    "return_lag_2",
    "sentiment_lag_2",
    "return_lag_3",
    "sentiment_lag_3",
    "return_lag_5",
    "sentiment_lag_5",
    "market_volatility",
    "high_volatility_regime",
    "high_vix_regime",
    "market_avg_return",
    "relative_strength",
    "future_close",
    "future_return",
    "future_return_rank",
    "TARGET_CLASS",
    "TARGET_REG",
]


def load_raw_data():
    print("Loading raw market data from AWS database...")
    query = 'SELECT * FROM raw_market_data ORDER BY "Date" ASC;'
    df = pd.read_sql(query, engine)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def calculate_macro_features(df):
    print("Calculating exact Macro & Sector features...")
    MACRO_TICKERS = {
        "SPY": "SPY",
        "QQQ": "QQQ",
        "VIX": "^VIX",
        "DXY": "DX-Y.NYB",
        "TNX": "^TNX",
        "OIL": "CL=F",
        "XLK": "XLK",
        "XLF": "XLF",
        "XLE": "XLE",
        "XLV": "XLV",
    }
    macro_configs = [
        ("SPY", True, True),
        ("QQQ", True, True),
        ("VIX", True, False),
        ("DXY", False, False),
        ("TNX", False, False),
        ("OIL", False, False),
        ("XLK", True, False),
        ("XLF", True, False),
        ("XLE", True, False),
        ("XLV", True, False),
    ]

    for prefix, req_5d, req_vol in macro_configs:
        ticker = MACRO_TICKERS[prefix]
        possible_cols = [
            f"{prefix}_Close",
            prefix,
            ticker,
            f"('{ticker}', 'Close')",
            f"('Close', '{ticker}')",
        ]

        actual_col = next((col for col in possible_cols if col in df.columns), None)

        if not actual_col:
            if prefix in ["VIX", "TNX"]:
                df[f"{prefix}_change_1d"] = 0.0
            else:
                df[f"{prefix}_return_1d"] = 0.0
            if req_5d or prefix == "VIX":
                df[f"{prefix}_return_5d"] = 0.0
            if req_vol:
                df[f"{prefix}_volatility"] = 0.0
            if prefix == "VIX":
                df["VIX_level"] = 0.0
            continue

        macro_series = df.groupby("Date")[actual_col].first().reset_index()

        if prefix in ["VIX", "TNX"]:
            macro_series[f"{prefix}_change_1d"] = macro_series[actual_col].diff()
        else:
            macro_series[f"{prefix}_return_1d"] = macro_series[actual_col].pct_change()

        if req_5d or prefix == "VIX":
            macro_series[f"{prefix}_return_5d"] = macro_series[actual_col].pct_change(5)
        if req_vol:
            macro_series[f"{prefix}_volatility"] = (
                macro_series[f"{prefix}_return_1d"].rolling(20).std()
            )
        if prefix == "VIX":
            macro_series["VIX_level"] = macro_series[actual_col]

        macro_series = macro_series.drop(columns=[actual_col])
        df = df.merge(macro_series, on="Date", how="left")

    return df


def calculate_technical_and_sentiment_features(df):
    print("Calculating technical indicators, lags, and exponential sentiment decay...")
    df["market_sentiment"] = df.groupby("Date")["sentiment_numeric"].transform("mean")
    df["market_news_count"] = df.groupby("Date")["news_count"].transform("sum")

    processed_dfs = []
    for symbol, group in df.groupby("Stock_symbol"):
        ticker_df = group.sort_values("Date").copy()

        ticker_df["daily_return"] = ticker_df["Close"].pct_change()
        ticker_df["return_3d"] = ticker_df["Close"].pct_change(3)
        ticker_df["return_7d"] = ticker_df["Close"].pct_change(7)

        delta = ticker_df["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = delta.where(delta < 0, 0).abs().rolling(14).mean()
        ticker_df["RSI"] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

        ticker_df["SMA_20"] = ticker_df["Close"].rolling(20).mean()
        ticker_df["SMA_50"] = ticker_df["Close"].rolling(50).mean()
        ticker_df["VOLATILITY_20"] = ticker_df["daily_return"].rolling(20).std()

        exp1 = ticker_df["Close"].ewm(span=12, adjust=False).mean()
        exp2 = ticker_df["Close"].ewm(span=26, adjust=False).mean()
        ticker_df["MACD"] = exp1 - exp2
        ticker_df["MACD_SIGNAL"] = ticker_df["MACD"].ewm(span=9, adjust=False).mean()

        for window in [3, 5, 10]:
            ticker_df[f"close_mean_{window}"] = (
                ticker_df["Close"].rolling(window).mean()
            )
            ticker_df[f"close_std_{window}"] = ticker_df["Close"].rolling(window).std()
            ticker_df[f"volume_mean_{window}"] = (
                ticker_df["Volume"].rolling(window).mean()
            )

        for lag in [1, 2, 3, 5]:
            ticker_df[f"return_lag_{lag}"] = ticker_df["daily_return"].shift(lag)
            ticker_df[f"sentiment_lag_{lag}"] = ticker_df["sentiment_numeric"].shift(
                lag
            )

        ticker_df["last_sentiment"] = (
            ticker_df["sentiment_numeric"].replace(0, np.nan).ffill().fillna(0)
        )
        ticker_df["days_since_news"] = ticker_df.groupby(
            (ticker_df["no_news_flag"] == 0).cumsum()
        ).cumcount()
        ticker_df["sentiment_decay"] = ticker_df["last_sentiment"] * np.exp(
            -0.1 * ticker_df["days_since_news"]
        )
        ticker_df["propagated_sentiment"] = ticker_df["sentiment_decay"]

        for window in [3, 7, 14]:
            ticker_df[f"sentiment_{window}d_avg"] = (
                ticker_df["sentiment_numeric"].rolling(window).mean()
            )

        ticker_df["sentiment_volatility_7d"] = (
            ticker_df["sentiment_numeric"].rolling(7).std()
        )
        ticker_df["news_count_3d"] = ticker_df["news_count"].rolling(3).sum()
        ticker_df["news_count_7d"] = ticker_df["news_count"].rolling(7).sum()
        ticker_df["no_news_ratio_7d"] = ticker_df["no_news_flag"].rolling(7).mean()

        processed_dfs.append(ticker_df)

    return pd.concat(processed_dfs, ignore_index=True)


def calculate_market_regimes_and_targets(df):
    print("Calculating market regimes and final targets...")
    market_return = (
        df.groupby("Date")["daily_return"].mean().rename("market_avg_return")
    )
    market_vol = df.groupby("Date")["VOLATILITY_20"].mean().rename("market_volatility")
    df = df.merge(market_return, on="Date", how="left").merge(
        market_vol, on="Date", how="left"
    )

    df["relative_strength"] = df["daily_return"] - df["market_avg_return"]
    df["high_volatility_regime"] = (
        df["VOLATILITY_20"] > df["market_volatility"] * 1.5
    ).astype(int)
    df["high_vix_regime"] = (
        (df["VIX_level"] > 25).astype(int) if "VIX_level" in df.columns else 0
    )

    df["earnings_cycle_day"] = 45
    df["days_to_earnings"] = 45
    df["earnings_window"] = 0

    # Targets (Horizon = 5)
    grouped = df.groupby("Stock_symbol")
    df["future_close"] = grouped["Close"].shift(-5)
    df["future_return"] = df["future_close"] / (df["Close"] + 1e-9) - 1
    df["future_return_rank"] = df.groupby("Date")["future_return"].rank(pct=True)

    df["TARGET_REG"] = df["future_return"]
    df["TARGET_CLASS"] = (
        (df["future_return"] >= 0.015) & (df["relative_strength"] > 0)
    ).astype(int)

    return df


def enforce_schema_and_save(df):
    print(f"\nEnforcing strict schema of {len(EXPECTED_COLUMNS)} columns...")
    df = df.ffill().bfill().fillna(0)

    try:
        final_df = df[EXPECTED_COLUMNS]
    except KeyError as e:
        print(f"CRITICAL ERROR: Missing column: {e}")
        return

    final_df.to_sql("deployment_dataset", con=engine, if_exists="replace", index=False)
    print("✅ Success! Dataset compiled and saved to AWS RDS.")


if __name__ == "__main__":
    df = load_raw_data()
    if not df.empty:
        df = calculate_macro_features(df)
        df = calculate_technical_and_sentiment_features(df)
        df = calculate_market_regimes_and_targets(df)
        enforce_schema_and_save(df)
    else:
        print("Error: raw_market_data table is empty.")

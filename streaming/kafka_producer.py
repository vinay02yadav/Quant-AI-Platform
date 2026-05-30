import os
import json
import time
import pandas as pd
import yfinance as yf
import feedparser
from kafka import KafkaProducer
import warnings
from dotenv import load_dotenv
from pathlib import Path

warnings.filterwarnings("ignore")
# Load .env from the root directory
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ==========================================
# STRICT .ENV CONFIGURATION
# ==========================================
KAFKA_IP = os.environ.get("KAFKA_BROKER_IP")
if not KAFKA_IP:
    raise ValueError("❌ KAFKA_BROKER_IP is missing from your .env file!")

KAFKA_PORT = os.environ.get("KAFKA_PORT", "9092")
KAFKA_BROKER = f"{KAFKA_IP}:{KAFKA_PORT}"
TOPIC_NAME = os.environ.get("KAFKA_TOPIC", "market_data_stream")
START_DATE = "2025-01-01"

# Uses local env fallback to support your specific Windows drive structure
ORIGINAL_DATASET_PATH = os.getenv(
    "ORIGINAL_DATASET_PATH",
    r"G:\.shortcut-targets-by-id\1g_KAklfRM3BgFWhlpys79RACiDr_cI7i\finance_ai\processed\final_training_dataset_temporal.parquet",
)

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


def get_rss_news(symbol):
    rss_url = f"https://finance.yahoo.com/rss/headline?s={symbol}"
    try:
        feed = feedparser.parse(rss_url)
        if feed.entries:
            headlines = [entry.title for entry in feed.entries[:3]]
            return " | ".join(headlines)
    except:
        pass
    return "No recent news."


def run_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        print(f"✅ Connected to EC2 Broker at {KAFKA_BROKER}")
    except Exception as e:
        print(f"❌ KAFKA CONNECTION FAILED: {e}")
        return

    # Extract Tickers
    try:
        df = pd.read_parquet(ORIGINAL_DATASET_PATH)
        tickers = df["Stock_symbol"].dropna().unique().tolist()
        print(f"Found {len(tickers)} tickers. Beginning stream...")
    except Exception as e:
        print(f"❌ Failed to load dataset from {ORIGINAL_DATASET_PATH}. Error: {e}")
        return

    # Fetch Macro Data
    macro_data = []
    for name, ticker in MACRO_TICKERS.items():
        try:
            hist = yf.download(ticker, start=START_DATE, progress=False)["Close"]
            if not hist.empty:
                hist.name = f"{name}_Close"
                macro_data.append(hist)
        except:
            pass

    if macro_data:
        macro_df = pd.concat(macro_data, axis=1)
        macro_df.index.name = "Date"
        macro_df = macro_df.reset_index()
        macro_df["Date"] = pd.to_datetime(macro_df["Date"]).dt.tz_localize(None)
    else:
        macro_df = pd.DataFrame()

    recent_date_threshold = pd.Timestamp.now() - pd.Timedelta(days=3)

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=START_DATE).reset_index()
            if df.empty:
                continue

            df = df.rename(columns={"index": "Date", "Datetime": "Date"})
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)

            if not macro_df.empty:
                df = df.merge(macro_df, on="Date", how="left")
            df = df.ffill().bfill().fillna(0)

            news_text = get_rss_news(ticker)

            # Stream row by row to Kafka
            for _, row in df.iterrows():
                payload = row.to_dict()
                payload["Stock_symbol"] = ticker
                payload["Date"] = payload["Date"].strftime("%Y-%m-%d")

                if pd.to_datetime(payload["Date"]) >= recent_date_threshold:
                    payload["daily_news_chunk"] = news_text
                    payload["news_count"] = (
                        0
                        if news_text == "No recent news."
                        else len(news_text.split(" | "))
                    )
                    payload["no_news_flag"] = 1 if payload["news_count"] == 0 else 0
                else:
                    payload["daily_news_chunk"] = ""
                    payload["news_count"] = 0
                    payload["no_news_flag"] = 1

                producer.send(TOPIC_NAME, payload)

            print(f"📡 Streamed data for {ticker} to Kafka.")
            time.sleep(0.5)

        except Exception as e:
            print(f"Error on {ticker}: {e}")

    producer.flush()
    print("✅ All data published. Producer shutting down.")


if __name__ == "__main__":
    run_producer()

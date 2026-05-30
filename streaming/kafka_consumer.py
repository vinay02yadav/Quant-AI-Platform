import os
import json
import requests
import pandas as pd
from kafka import KafkaConsumer
from sqlalchemy import create_engine
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

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# HUGGING FACE API CONFIG
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}" if HF_API_TOKEN else ""}
FINBERT_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
QWEN_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-0.5B-Instruct"


def query_hf_api(api_url, payload):
    try:
        response = requests.post(api_url, headers=HEADERS, json=payload, timeout=15)
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None


def run_consumer():
    print("\n🧠 Initializing Serverless AI Models (FinBERT & Qwen via API)...")

    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="quant_ai_group",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )
        print(f"✅ Connected to EC2 Broker at {KAFKA_BROKER}")
    except Exception as e:
        print(f"❌ KAFKA CONNECTION FAILED: {e}")
        return

    print(f"🎧 Listening to Kafka Topic: '{TOPIC_NAME}'...")

    buffer = []
    BUFFER_SIZE = 50  # Write to DB in batches for performance

    for message in consumer:
        data = message.value
        symbol = data.get("Stock_symbol")
        news_text = data.get("daily_news_chunk", "")

        # Defaults
        data["qwen_market_summary"] = "No news"
        data["sentiment_score"] = 0.0
        data["sentiment_label"] = "NEUTRAL"
        data["sentiment_numeric"] = 0.0

        if data.get("news_count", 0) > 0 and HF_API_TOKEN:
            try:
                # Serverless FinBERT
                fb_result = query_hf_api(FINBERT_URL, {"inputs": news_text[:512]})
                if fb_result and isinstance(fb_result, list) and len(fb_result) > 0:
                    top_pred = max(fb_result[0], key=lambda x: x["score"])
                    label = top_pred["label"]
                    score = top_pred["score"]

                    data["sentiment_score"] = (
                        score
                        if label.lower() == "positive"
                        else (-score if label.lower() == "negative" else 0.0)
                    )
                    data["sentiment_label"] = label.upper()
                    data["sentiment_numeric"] = data["sentiment_score"]

                # Serverless Qwen
                qwen_prompt = f"<|im_start|>system\nSummarize the following financial headlines in one short sentence.<|im_end|>\n<|im_start|>user\n{news_text[:500]}<|im_end|>\n<|im_start|>assistant\n"
                qw_result = query_hf_api(
                    QWEN_URL,
                    {"inputs": qwen_prompt, "parameters": {"max_new_tokens": 30}},
                )

                if qw_result and isinstance(qw_result, list) and len(qw_result) > 0:
                    gen_text = qw_result[0].get("generated_text", "")
                    if "assistant\n" in gen_text:
                        data["qwen_market_summary"] = gen_text.split("assistant\n")[
                            -1
                        ].strip()
                    else:
                        data["qwen_market_summary"] = gen_text[:100].strip()

                print(
                    f"[{symbol}] AI Processed: {data['sentiment_label']} ({data['sentiment_numeric']:.2f})"
                )
            except Exception as e:
                print(f"AI Error on {symbol}: {e}")

        buffer.append(data)

        if len(buffer) >= BUFFER_SIZE:
            df = pd.DataFrame(buffer)

            # --- FIX: Strip out unwanted yfinance columns ---
            unwanted = ["Dividends", "Stock Splits"]
            df = df.drop(
                columns=[c for c in unwanted if c in df.columns], errors="ignore"
            )

            df.to_sql("raw_market_data", con=engine, if_exists="append", index=False)
            print(f"💾 Committed batch of {BUFFER_SIZE} records to AWS RDS Database.")
            buffer = []


if __name__ == "__main__":
    run_consumer()

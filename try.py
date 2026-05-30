import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Build the connection string from your .env
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)


def check_database():
    print("🔍 Connecting to AWS RDS...")
    try:
        # 1. Fetch total row count
        count_query = "SELECT COUNT(*) FROM raw_market_data;"
        total_rows = pd.read_sql(count_query, engine).iloc[0, 0]
        print(f"\n✅ SUCCESS: Found {total_rows} total rows in 'raw_market_data'.\n")

        # 2. Fetch the column names (labels)
        cols_query = "SELECT * FROM raw_market_data LIMIT 0;"
        columns = pd.read_sql(cols_query, engine).columns.tolist()
        print("📊 Table Columns:")
        for col in columns:
            print(f" - {col}")

        # 3. Fetch a quick sample of the latest 5 rows
        print("\n📝 Latest 5 Entries:")
        sample_query = 'SELECT "Date", "Stock_symbol", "Close", "sentiment_label" FROM raw_market_data ORDER BY "Date" DESC LIMIT 5;'
        sample_df = pd.read_sql(sample_query, engine)
        print(sample_df.to_string(index=False))

    except Exception as e:
        print(f"\n❌ ERROR querying database: {e}")


if __name__ == "__main__":
    check_database()

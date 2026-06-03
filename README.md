# Quant AI Platform

A full-stack quantitative market intelligence platform for generating multi-horizon equity forecasts, ranking trading opportunities, and visualizing model performance through a production-style dashboard.

**Live Dashboard:** https://quant-ai-platform.vercel.app/

---

## Overview

Quant AI Platform combines market data, news sentiment, feature engineering, machine learning, streaming infrastructure, and a web dashboard into one end-to-end quantitative research pipeline.

The system uses a MultiOutput LightGBM model to forecast multiple return horizons and generate ranked market signals. The frontend dashboard displays live health checks, top signals, market analytics, model metadata, strategy performance, and MLflow experiment metrics.

For a detailed explanation of the architecture, model design, feature engineering, and deployment workflow, refer to the project PDF included in this repository.

---

## Architecture

![Quant Pipeline Architecture](docs/quant-pipeline-architecture-flowchart.png)

At a high level, the platform includes:

- Kafka-based market data streaming
- PostgreSQL storage for raw data, engineered features, predictions, and signals
- AI/NLP processing for financial news sentiment
- LightGBM multi-horizon forecasting
- MLflow experiment tracking
- FastAPI backend APIs
- Next.js dashboard frontend

---

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI, Uvicorn, SQLAlchemy, Pandas |
| Machine Learning | LightGBM, Scikit-learn, MLflow, Joblib |
| Streaming | Apache Kafka, Kafka Python |
| Database | PostgreSQL |
| Data Sources | Yahoo Finance, RSS news feeds, Hugging Face APIs |
| Infrastructure | Docker, Docker Compose, AWS/GCP configs, Vercel |

---

## Key Features

- Multi-horizon forecasting for 1-day, 3-day, and 5-day return targets
- LightGBM MultiOutput model for equity prediction
- Technical indicators, macro features, sector features, and sentiment features
- FinBERT-based financial news sentiment scoring
- AI-generated market summaries using Hugging Face inference APIs
- Kafka streaming pipeline for market data ingestion
- PostgreSQL-backed data storage
- MLflow model metric tracking
- FastAPI backend for serving dashboard data
- Next.js dashboard for market intelligence visualization

---

## Quick Start

Run the project locally with two terminals: one for the backend API and one for the frontend dashboard.

### 1. Start the Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

### 2. Start the Frontend

Open a new terminal:

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

---

## Environment Variables

Create a `.env` file in the root directory before running the backend or pipeline scripts.

```env
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=quant_db

DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@your_database_host:5432/quant_db

NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

GCP_EXTERNAL_IP=127.0.0.1

KAFKA_BROKER_IP=127.0.0.1
KAFKA_PORT=9092
KAFKA_TOPIC=market_data_stream

HF_API_TOKEN=your_hugging_face_token
```


---

## Repository Structure

```text
quant-pipeline/
├── backend/
│   ├── routers/
│   │   ├── predictions.py
│   │   └── signals.py
│   ├── services/
│   ├── app.py
│   ├── database.py
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   ├── migrations/
│   └── init.sql
├── docs/
│   ├── quant-pipeline-architecture-flowchart.png
│   └── quant-pipeline-architecture-flowchart.svg
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── services/
│   ├── types/
│   ├── package.json
│   └── next.config.ts
├── infrastructure/
│   ├── aws-docker-compose.yml
│   └── gcp-docker-compose.yml
├── ml_engine/
│   ├── models/
│   ├── feature_engineer.py
│   ├── predictor.py
│   ├── requirements.txt
│   ├── run_inference.py
│   └── train.py
├── streaming/
│   ├── Dockerfile
│   ├── kafka_consumer.py
│   ├── kafka_producer.py
│   └── requirements.txt
└── README.md
```

---

## Project Documentation

This README provides a clean project overview and simple local startup instructions.

For a deeper explanation of the system, refer to the detailed project PDF included in the repository. The PDF covers:

- Full architecture design
- Data pipeline workflow
- Feature engineering process
- Machine learning methodology
- Model training and inference logic
- Cloud deployment approach
- Dashboard and API behavior

---

## Security Notes

This repository is configured to ignore sensitive and generated files such as:

- `.env`
- `.env.*`
- `kafka-key.pem`
- virtual environments
- Next.js build output
- MLflow local data
- model pickle files
- Python cache files

Before pushing to GitHub, confirm that no secrets, private keys, local databases, or generated artifacts are tracked.

---

## Author

**Vinay Yadav**

---

## Disclaimer

This project is for educational and research purposes only. It does not provide financial advice, investment recommendations, or guaranteed trading performance.

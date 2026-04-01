# Finance AI Platform

FastAPI backend + Streamlit UI for:
- Fraud detection
- Credit risk scoring
- Spending profile classification

This project combines multiple financial ML models behind a single API and Streamlit interface so you can analyze transactions, classify spending behavior, and estimate credit-related outcomes in one place.

## Features

- Fraud detection for suspicious transaction patterns
- Spending profile classification
- Credit score prediction
- Unified agent-style interface across models

## Prerequisites

- Python 3.10+ recommended
- Ollama installed and running
- Ollama model available: `qwen2.5:7b`

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run Backend

```powershell
python -m uvicorn app.main:app --reload
```

Backend health check:

```powershell
curl http://127.0.0.1:8000/
```

## Run UI

In another terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run agent_ui.py
```

## Optional Environment Variables

- `API_BASE_URL` default: `http://127.0.0.1:8000`
- `LLM_MODEL` default: `qwen2.5:7b`

Example:

```powershell
$env:API_BASE_URL="http://127.0.0.1:8000"
$env:LLM_MODEL="qwen2.5:7b"
streamlit run agent_ui.py
```

## Project Files

- `app/main.py`
- `app/schemas.py`
- `agent_ui.py`
- `models/credit_model.joblib`
- `models/fraud_model.joblib`
- `models/spending_model.joblib`

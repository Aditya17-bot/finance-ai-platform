from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import time

from .schemas import (
    AgentInput, AgentResponse,
    FraudInput, CreditInput, SpendingLiteInput, Transaction
)

# =====================================================
# LOGGING
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("FinanceAI")

# =====================================================
# PATH SETUP
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"

# =====================================================
# APP INIT
# =====================================================
app = FastAPI(
    title="Finance AI Platform",
    description="""
## 🏦 Agentic AI for Financial Intelligence

A production-grade AI system for:
- 🚨 **Fraud Detection** — Real-time transaction risk analysis
- 📊 **Spending Classification** — Behavioral spending profile
- 💳 **Credit Scoring** — ML-based creditworthiness prediction
- 🤖 **Agent Orchestration** — Unified multi-model intelligence layer

> Built with FastAPI + scikit-learn. All models are pre-trained `.joblib` files.
    """,
    version="3.0",
    docs_url=None,
    contact={
        "name": "Finance AI Team",
        "email": "financeai@example.com"
    },
    license_info={
        "name": "MIT",
    }
)

# =====================================================
# CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# REQUEST TIMING MIDDLEWARE
# =====================================================
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(duration)
    return response

# =====================================================
# MODELS REGISTRY
# =====================================================
models = {}

# =====================================================
# CREDIT SCORE HELPERS
# =====================================================
def get_risk_band(score: int) -> tuple[str, str]:
    """Returns (risk_band, recommendation) from credit score."""
    if score >= 750:
        return "Excellent", "Eligible for premium credit products and lowest interest rates."
    elif score >= 700:
        return "Good", "Eligible for most credit products. Minor improvements can unlock better rates."
    elif score >= 650:
        return "Fair", "Credit available with moderate interest. Focus on reducing utilization."
    elif score >= 600:
        return "Poor", "Limited credit access. Prioritize on-time payments and reducing debt."
    else:
        return "Very Poor", "High risk profile. Consider secured credit or financial counseling."


def get_fraud_risk_level(pred: int, velocity: int, location_change: int) -> str:
    """Contextual fraud risk level."""
    if pred == 1:
        if velocity >= 6 or location_change == 1:
            return "CRITICAL"
        return "HIGH"
    elif velocity >= 4:
        return "MEDIUM"
    return "LOW"


# =====================================================
# LOAD MODELS ON STARTUP
# =====================================================
@app.on_event("startup")
async def startup_event():
    log.info(f"Loading models from: {MODEL_DIR}")

    model_files = {
        "fraud": "fraud_model.joblib",
        "spending": "spending_model.joblib",
        "credit": "credit_model.joblib",
    }

    for key, filename in model_files.items():
        path = MODEL_DIR / filename
        try:
            models[key] = joblib.load(path)
            log.info(f"[OK] '{key}' model loaded — {path.name}")
        except FileNotFoundError:
            log.error(f"[MISSING] {path} not found.")
        except Exception as e:
            log.error(f"[ERROR] Failed to load '{key}' model: {e}")

    loaded = list(models.keys())
    log.info(f"Startup complete. Models ready: {loaded}")


# =====================================================
# DOCS ROUTE (Custom Swagger)
# =====================================================
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Finance AI Platform — API Docs",
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "defaultModelsExpandDepth": 2,
            "syntaxHighlight.theme": "monokai",
        }
    )


# =====================================================
# ROOT
# =====================================================
@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Finance AI Platform",
        "version": "3.0",
        "status": "running" if models else "degraded",
        "loaded_models": list(models.keys()),
        "missing_models": [k for k in ["fraud", "spending", "credit"] if k not in models],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
def health():
    all_loaded = all(k in models for k in ["fraud", "spending", "credit"])
    return {
        "healthy": all_loaded,
        "models": {k: k in models for k in ["fraud", "spending", "credit"]}
    }


# =====================================================
# FRAUD DETECTION
# =====================================================
@app.post("/fraud/detect", tags=["Fraud Detection"], summary="Detect fraudulent transactions")
def detect_fraud(data: dict):
    """
    Analyzes a single transaction for fraud risk using ML classification.

    Required fields: `amount`, `hour`, `location_change`, `merchant_type`, `txn_velocity`
    """
    model = models.get("fraud")
    if not model:
        raise HTTPException(503, detail="Fraud detection model is not loaded.")

    required = ["amount", "hour", "location_change", "merchant_type", "txn_velocity"]
    missing = [f for f in required if f not in data]
    if missing:
        raise HTTPException(422, detail=f"Missing required fields: {missing}")

    try:
        features = [[
            float(data["amount"]),
            int(data["hour"]),
            int(data["location_change"]),
            int(data["merchant_type"]),
            int(data["txn_velocity"])
        ]]

        pred = int(model.predict(features)[0])
        risk_level = get_fraud_risk_level(pred, data["txn_velocity"], data["location_change"])

        return {
            "is_fraud": bool(pred),
            "status": "FRAUD 🚨" if pred == 1 else "SAFE ✅",
            "risk_level": risk_level,
            "transaction_amount": data["amount"],
            "analyzed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        log.error(f"Fraud detection error: {e}")
        raise HTTPException(500, detail=str(e))


# =====================================================
# SPENDING CLASSIFICATION
# =====================================================
@app.post("/spending/predict", tags=["Spending Analysis"], summary="Classify spending behavior")
def predict_spending(data: dict):
    """
    Classifies a user's spending profile based on category ratios.

    Ratios should be between 0.0–1.0 and ideally sum to ~1.0.
    """
    model = models.get("spending")
    if not model:
        raise HTTPException(503, detail="Spending classification model is not loaded.")

    required = ["food_ratio", "rent_ratio", "luxury_ratio", "investment_ratio", "misc_ratio"]
    missing = [f for f in required if f not in data]
    if missing:
        raise HTTPException(422, detail=f"Missing required fields: {missing}")

    try:
        ratios = {k: float(data[k]) for k in required}
        features = [list(ratios.values())]
        prediction = str(model.predict(features)[0])

        # Dominant category detection
        dominant_category = max(ratios, key=ratios.get).replace("_ratio", "").title()

        return {
            "spending_type": prediction,
            "dominant_category": dominant_category,
            "category_ratios": ratios,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        log.error(f"Spending classification error: {e}")
        raise HTTPException(500, detail=str(e))


# =====================================================
# CREDIT SCORING
# =====================================================
@app.post("/credit/predict", tags=["Credit Scoring"], summary="Predict credit score")
def predict_credit(data: dict):
    """
    Predicts a credit score using financial behavior features.

    Required: `monthly_spend`, `credit_utilization`, `late_payments`,
              `num_transactions`, `discretionary_ratio`
    """
    model = models.get("credit")
    if not model:
        raise HTTPException(503, detail="Credit scoring model is not loaded.")

    required = ["monthly_spend", "credit_utilization", "late_payments", "num_transactions", "discretionary_ratio"]
    missing = [f for f in required if f not in data]
    if missing:
        raise HTTPException(422, detail=f"Missing required fields: {missing}")

    try:
        features = [[
            float(data["monthly_spend"]),
            float(data["credit_utilization"]),
            int(data["late_payments"]),
            int(data["num_transactions"]),
            float(data["discretionary_ratio"])
        ]]

        score = int(model.predict(features)[0])
        risk_band, recommendation = get_risk_band(score)

        return {
            "credit_score": score,
            "risk_band": risk_band,
            "recommendation": recommendation,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        log.error(f"Credit scoring error: {e}")
        raise HTTPException(500, detail=str(e))


# =====================================================
# AGENT — FULL ORCHESTRATION
# =====================================================
@app.post("/agent/analyze-user", tags=["AI Agent"], summary="Full agentic financial analysis")
def analyze_user(data: AgentInput):
    """
    🤖 The full AI agent pipeline — orchestrates all three models in sequence:

    1. **Spending Analysis** — Aggregates transactions into category ratios → classifies spending type
    2. **Credit Scoring** — Derives credit features from spending patterns → predicts credit score
    3. **Fraud Detection** — Analyzes most recent transaction → flags suspicious activity

    Returns consolidated insights with actionable recommendations.
    """
    missing_models = [k for k in ["fraud", "spending", "credit"] if k not in models]
    if missing_models:
        raise HTTPException(503, detail=f"Required models not loaded: {missing_models}")

    try:
        transactions = data.transactions
        credit_limit = data.credit_limit

        # ─────────────────────────────────────────────
        # STEP 1: Aggregate spending by category
        # ─────────────────────────────────────────────
        category_totals: dict = {}
        for txn in transactions:
            cat = txn.category
            category_totals[cat] = category_totals.get(cat, 0) + txn.amount

        total_spend = sum(category_totals.values())
        if total_spend == 0:
            raise HTTPException(400, detail="Total transaction spend cannot be zero.")

        spending_ratios = {
            cat: round(category_totals.get(cat, 0) / total_spend, 4)
            for cat in ["Food", "Rent", "Luxury", "Investment", "Misc"]
        }

        # ─────────────────────────────────────────────
        # STEP 2: Spending Classification
        # ─────────────────────────────────────────────
        spending_features = [list(spending_ratios.values())]
        spending_type = str(models["spending"].predict(spending_features)[0])
        dominant_category = max(spending_ratios, key=spending_ratios.get)

        # ─────────────────────────────────────────────
        # STEP 3: Credit Scoring
        # ─────────────────────────────────────────────
        discretionary = spending_ratios.get("Luxury", 0) + spending_ratios.get("Food", 0)
        credit_features = [[
            total_spend,
            round(total_spend / credit_limit, 4),
            1,  # conservative: assume 1 late payment for demo
            len(transactions),
            round(discretionary, 4)
        ]]
        credit_score = int(models["credit"].predict(credit_features)[0])
        risk_band, recommendation = get_risk_band(credit_score)

        # ─────────────────────────────────────────────
        # STEP 4: Fraud Detection (most recent transaction)
        # ─────────────────────────────────────────────
        last_txn = transactions[-1]
        fraud_features = [[
            last_txn.amount,
            last_txn.hour,
            last_txn.location_change,
            last_txn.merchant_type,
            last_txn.txn_velocity
        ]]
        fraud_pred = int(models["fraud"].predict(fraud_features)[0])
        risk_level = get_fraud_risk_level(fraud_pred, last_txn.txn_velocity, last_txn.location_change)

        # ─────────────────────────────────────────────
        # STEP 5: Generate Insights
        # ─────────────────────────────────────────────
        insights = []

        # Spending insights
        if spending_type in ["Overspender", "High Spender"]:
            insights.append(f"⚠️ Overspending detected — {dominant_category} is your dominant category ({spending_ratios[dominant_category]*100:.1f}% of spend)")
        if spending_ratios.get("Investment", 0) == 0:
            insights.append("📉 No investment activity detected — consider allocating savings")
        if spending_ratios.get("Luxury", 0) > 0.4:
            insights.append(f"💸 Luxury spending is high at {spending_ratios['Luxury']*100:.1f}% — consider reducing discretionary expenses")

        # Credit insights
        if credit_score < 600:
            insights.append(f"🔴 Credit score is critically low ({credit_score}) — immediate action required")
        elif credit_score < 650:
            insights.append(f"🟡 Credit risk is rising ({credit_score}) — avoid new debt and pay on time")
        elif credit_score >= 750:
            insights.append(f"🟢 Excellent credit score ({credit_score}) — you qualify for premium products")

        if total_spend / credit_limit > 0.7:
            insights.append(f"⚡ High credit utilization ({(total_spend/credit_limit)*100:.1f}%) — aim to keep it below 30%")

        # Fraud insights
        if fraud_pred == 1:
            insights.append(f"🚨 FRAUD ALERT — Last transaction flagged as {risk_level} risk. Immediate review recommended.")
        elif last_txn.txn_velocity >= 5:
            insights.append(f"👀 Elevated transaction velocity ({last_txn.txn_velocity}/hr) — monitoring for unusual patterns")

        if not insights:
            insights.append("✅ Financial behavior is healthy — keep up the good work!")

        # ─────────────────────────────────────────────
        # STEP 6: Risk Summary
        # ─────────────────────────────────────────────
        if fraud_pred == 1 or credit_score < 600:
            risk_summary = "HIGH RISK — Immediate financial review recommended."
        elif credit_score < 650 or spending_type == "Overspender":
            risk_summary = "MODERATE RISK — Financial behavior needs improvement."
        else:
            risk_summary = "LOW RISK — Profile appears financially stable."

        return {
            "spending_type": spending_type,
            "spending_breakdown": spending_ratios,
            "dominant_category": dominant_category,
            "credit_score": credit_score,
            "risk_band": risk_band,
            "credit_recommendation": recommendation,
            "fraud_status": "FRAUD 🚨" if fraud_pred == 1 else "SAFE ✅",
            "fraud_risk_level": risk_level,
            "total_spend": round(total_spend, 2),
            "credit_utilization": round(total_spend / credit_limit, 4),
            "insights": insights,
            "risk_summary": risk_summary,
            "num_transactions": len(transactions),
            "analyzed_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Agent analysis error: {e}")
        raise HTTPException(500, detail=f"Agent error: {str(e)}")

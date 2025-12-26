from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

from app.schemas import CreditInput, FraudInput, SpendingLiteInput

# =====================================================
# PATH SETUP
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"

# =====================================================
# APP INIT
# =====================================================
app = FastAPI(
    title="Finance AI Platform",
    description="Finance AI Core with Fraud, Credit & Spending Intelligence",
    version="2.0",
    docs_url=None
)

models = {}

# =====================================================
# LOAD MODELS
# =====================================================
def load_all_models():
    print(f"🔍 Loading models from: {MODEL_DIR}")

    # 1️⃣ Credit Model
    try:
        models["credit"] = joblib.load(MODEL_DIR / "heloc_credit_model.joblib")
        print("✅ Credit model loaded")
    except Exception as e:
        print(f"❌ Credit model error: {e}")

    # 2️⃣ NEW Spending Profile Model (Lite)
    try:
        models["spending_lite"] = joblib.load(
            MODEL_DIR / "spending_profile_model.joblib"
        )
        models["spending_lite_features"] = joblib.load(
            MODEL_DIR / "spending_profile_features.joblib"
        )
        print("✅ Spending-lite model loaded")
    except Exception as e:
        print(f"❌ Spending-lite model error: {e}")

    # 3️⃣ Fraud Model Package
    try:
        models["fraud_package"] = joblib.load(
            MODEL_DIR / "fraud_model_package.joblib"
        )
        print("✅ Fraud package loaded")
    except Exception as e:
        print(f"❌ Fraud package error: {e}")


load_all_models()

# =====================================================
# FRAUD PREPROCESSING
# =====================================================
def preprocess_fraud(data: FraudInput, package):
    feature_list = package["features"]
    mappings = package.get("mappings", {})

    df = pd.DataFrame([data.dict(by_alias=True)])

    # Distance
    df["dist"] = np.sqrt(
        (df["lat"] - df["merch_lat"]) ** 2 +
        (df["long"] - df["merch_long"]) ** 2
    )

    # Time
    trans_time = pd.to_datetime(data.trans_date_trans_time)
    df["hour"] = trans_time.hour
    df["day_of_week"] = trans_time.dayofweek
    df["unix_time"] = trans_time.timestamp()

    # Age
    dob = pd.to_datetime(data.dob)
    df["age"] = (trans_time - dob).days // 365

    # Categoricals
    for col in ["category", "gender", "job"]:
        if col in mappings:
            df[col] = df[col].map(mappings[col]).fillna(0).astype(int)

    return df[feature_list]

# =====================================================
# ROUTES
# =====================================================
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Docs"
    )

@app.get("/")
def root():
    return {
        "status": "running",
        "loaded_models": list(models.keys())
    }

# =====================================================
# CREDIT ENDPOINT (UNCHANGED)
# =====================================================
@app.post("/credit-score/predict", tags=["Credit"])
def predict_credit(data: CreditInput):
    model = models.get("credit")
    if not model:
        raise HTTPException(503, "Credit model not loaded")

    features = np.array(list(data.dict().values())).reshape(1, -1)
    prob_bad = model.predict_proba(features)[0][1]

    bucket = (
        "HIGH" if prob_bad >= 0.67
        else "MEDIUM" if prob_bad >= 0.33
        else "LOW"
    )

    return {
        "probability_bad": round(float(prob_bad), 4),
        "risk_bucket": bucket
    }

# =====================================================
# 💤 OLD SPENDING MODEL (DEPRECATED)
# =====================================================
"""
@app.post("/spending-behavior/predict", tags=["Spending (Legacy)"])
def predict_spending(data: SpendingInput):
    LEGACY endpoint.
    Deprecated due to excessive input requirements.
"""
# =====================================================

# =====================================================
# 🆕 SPENDING LITE ENDPOINT
# =====================================================
@app.post("/spending-lite/predict", tags=["Spending"])
def predict_spending_lite(data: SpendingLiteInput):

    model = models.get("spending_lite")
    feature_list = models.get("spending_lite_features")

    if not model or not feature_list:
        raise HTTPException(503, "Spending-lite model not loaded")

    # Convert input to DataFrame
    df = pd.DataFrame([data.dict()])

    # One-hot encode city_type
    df = pd.get_dummies(df, columns=["city_type"])

    # Ensure all expected columns exist
    for col in feature_list:
        if col not in df:
            df[col] = 0

    # Reorder columns
    df = df[feature_list]

    prediction = model.predict(df)[0]
    probs = model.predict_proba(df)[0]

    return {
        "spending_profile": prediction,
        "confidence_scores": {
            cls: round(float(prob), 4)
            for cls, prob in zip(model.classes_, probs)
        }
    }

# =====================================================
# FRAUD ENDPOINT (UNCHANGED)
# =====================================================
@app.post("/fraud/detect", tags=["Fraud"])
def detect_fraud(data: FraudInput):
    package = models.get("fraud_package")
    if not package:
        raise HTTPException(503, "Fraud package not loaded")

    try:
        processed_df = preprocess_fraud(data, package)

        cb_prob = package["cb_model"].predict_proba(processed_df)[0][1]
        xgb_prob = package["xgb_model"].predict_proba(processed_df)[0][1]
        fraud_probability = (cb_prob + xgb_prob) / 2

        status = (
            "FRAUDULENT" if fraud_probability > 0.8
            else "SUSPICIOUS" if fraud_probability > 0.5
            else "LEGITIMATE"
        )

        return {
            "status": status,
            "fraud_probability": round(float(fraud_probability), 4),
            "details": {
                "dist": round(float(processed_df["dist"].iloc[0]), 2),
                "age": int(processed_df["age"].iloc[0])
            }
        }

    except Exception as e:
        raise HTTPException(500, str(e))

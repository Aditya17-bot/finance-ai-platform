from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from app.schemas import CreditInput, SpendingInput, FraudInput  # Changed 'app.schemas' to 'schemas' because you are in the same folder

# --- DYNAMIC PATH SETUP ---
# Since main.py is INSIDE 'app', the model folder is just 'model' in the same directory
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"

# --- APP INITIALIZATION ---
app = FastAPI(
    title="Finance AI Platform",
    description="Finance AI Core with Ensemble Fraud Detection.",
    version="1.3",
    docs_url=None 
)

models = {}
spending_class_map = {0: "High", 1: "Low", 2: "Medium"}

def load_all_models():
    """Loads all models from the model directory"""
    print(f"🔍 Searching for models in: {MODEL_DIR}")
    
    # 1. Credit Model
    try:
        models["credit"] = joblib.load(MODEL_DIR / "heloc_credit_model.joblib")
        print("✅ Credit Model Loaded Successfully")
    except Exception as e:
        print(f"❌ Credit Model Error: {e}")

    # 2. Spending Model
    try:
        models["spending"] = joblib.load(MODEL_DIR / "spending_behavior_model.joblib")
        print("✅ Spending Model Loaded Successfully")
    except Exception as e:
        print(f"❌ Spending Model Error: {e}")

    # 3. Fraud Model Package (MATCHING YOUR SCREENSHOT NAME)
    try:
        models["fraud_package"] = joblib.load(MODEL_DIR / "fraud_model_package.joblib")
        print("✅ Fraud Package Loaded Successfully")
    except Exception as e:
        print(f"❌ Fraud Package Error: {e}")

# Run the loader
load_all_models()

# ==========================================
#  FRAUD PREPROCESSING LOGIC
# ==========================================
def preprocess_fraud(data: FraudInput, package):
    feature_list = package['features']
    mappings = package.get('mappings', {}) 
    
    # Convert Pydantic to DataFrame
    df = pd.DataFrame([data.dict(by_alias=True)])
    
    # Distance Engineering
    df['dist'] = np.sqrt((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)
    
    # Time Engineering
    trans_time = pd.to_datetime(data.trans_date_trans_time)
    df['hour'] = trans_time.hour
    df['day_of_week'] = trans_time.dayofweek
    df['unix_time'] = trans_time.timestamp()
    
    # Age Engineering
    dob = pd.to_datetime(data.dob)
    df['age'] = (trans_time - dob).days // 365
    
    # Categorical Mapping
    for col in ['category', 'gender', 'job']:
        if col in mappings:
            df[col] = df[col].map(mappings[col]).fillna(0).astype(int)
    
    return df[feature_list]

# ==========================================
#  ENDPOINTS
# ==========================================

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Documentation"
    )

@app.get("/")
def root():
    return {
        "message": "Finance AI Platform is active!",
        "loaded_models": list(models.keys())
    }

@app.post("/credit-score/predict", tags=["Credit Scoring"])
def predict_credit(data: CreditInput):
    if "credit" not in models:
        raise HTTPException(status_code=503, detail="Credit model not loaded")
    features = np.array(list(data.dict().values())).reshape(1, -1)
    prob_bad = models["credit"].predict_proba(features)[0][1]
    bucket = "HIGH" if prob_bad >= 0.67 else "MEDIUM" if prob_bad >= 0.33 else "LOW"
    return {"probability_bad": round(float(prob_bad), 4), "risk_bucket": bucket}

@app.post("/spending-behavior/predict", tags=["Spending Analysis"])
def predict_spending(data: SpendingInput):
    if "spending" not in models:
        raise HTTPException(status_code=503, detail="Spending model not loaded")
    input_df = pd.DataFrame([data.dict(by_alias=True)])
    prediction_idx = int(models["spending"].predict(input_df)[0])
    probs = models["spending"].predict_proba(input_df)[0]
    return {
        "predicted_class": spending_class_map.get(prediction_idx, "Unknown"),
        "confidence_scores": [round(float(p), 4) for p in probs]
    }

@app.post("/fraud/detect", tags=["Fraud Detection"])
def detect_fraud(data: FraudInput):
    package = models.get("fraud_package")
    if not package:
        raise HTTPException(status_code=503, detail="Fraud package not loaded")
    try:
        processed_df = preprocess_fraud(data, package)
        cb_prob = package['cb_model'].predict_proba(processed_df)[0][1]
        xgb_prob = package['xgb_model'].predict_proba(processed_df)[0][1]
        fraud_probability = (cb_prob + xgb_prob) / 2
        
        status = "FRAUDULENT" if fraud_probability > 0.8 else "SUSPICIOUS" if fraud_probability > 0.5 else "LEGITIMATE"
        
        return {
            "status": status,
            "fraud_probability": round(float(fraud_probability), 4),
            "details": {
                "dist": round(float(processed_df['dist'].iloc[0]), 2),
                "age": int(processed_df['age'].iloc[0])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
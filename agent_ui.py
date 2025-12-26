import streamlit as st
import requests
import json
import re
from datetime import datetime
from langchain_community.chat_models import ChatOllama

# =====================================================
# CONFIG
# =====================================================
API_BASE_URL = "http://127.0.0.1:8000"
LLM_MODEL = "qwen2.5:7b"

# =====================================================
# LLM (Reasoning / Extraction ONLY)
# =====================================================
llm = ChatOllama(model=LLM_MODEL, temperature=0)

# =====================================================
# MOCK USER PROFILE (acts like DB / KYC)
# =====================================================
USER_PROFILE = {
    "lat": 12.9716,
    "long": 77.5946,
    "city": "Bangalore",
    "state": "KA",
    "zip": 560001,
    "city_pop": 10000000,
    "job": "Engineer",
    "dob": "1995-01-01",
    "avg_amt": 2500,
    "age": 30,
    "household_size": 3,
    "monthly_income": 60000,
    "owns_house": 0,
    "owns_vehicle": 1,
    "city_type": "urban"
}

CITY_COORDS = {
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.7041, 77.1025),
    "new york": (40.7128, -74.0060),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867)
}

# =====================================================
# STREAMLIT UI
# =====================================================
st.set_page_config(page_title="AI Financial Agent", page_icon="💰")
st.title("🤖 Financial AI Agent")

# =====================================================
# HELPERS
# =====================================================

def detect_intent(user_text: str) -> str:
    prompt = f"""
Classify the user request into ONE category.

fraud:
- fraud
- suspicious
- unauthorized
- scam

credit:
- credit score
- loan
- credit risk

spending:
- spending
- expenses
- budget

User message:
\"\"\"{user_text}\"\"\"

Reply with ONE WORD only:
fraud, credit, spending, or unknown
"""
    resp = llm.invoke(prompt)
    text = resp.content.lower()

    if any(k in text for k in ["fraud", "suspicious", "unauthorized", "scam"]):
        return "fraud"
    if any(k in text for k in ["credit", "loan", "risk"]):
        return "credit"
    if any(k in text for k in ["spending", "expense", "budget"]):
        return "spending"
    return "unknown"


# ---------------- AMOUNT NORMALIZATION ----------------
def normalize_amount(text: str):
    """
    ₹1,85,000 → 185000
    $2,300 → 2300
    """
    match = re.search(r"[₹$]?\s*([\d,]+)", text)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except Exception:
        return None


# ---------------- TRANSACTION EXTRACTION ----------------
def extract_transaction_info(user_text: str) -> dict:
    prompt = f"""
You are a STRICT information extraction engine.

Extract transaction details.
Return ONLY valid JSON.
If not mentioned, use null.

Rules:
- amt must be a NUMBER (no commas, no currency symbols)
- Convert ₹1,85,000 → 185000
- time_hint must be HH:MM (24-hour)

Fields:
- amt
- merchant_city
- time_hint

Text:
\"\"\"{user_text}\"\"\"
"""
    resp = llm.invoke(prompt)

    try:
        return json.loads(resp.content)
    except Exception:
        return {}

def detect_city_from_text(text: str):
    text = text.lower()
    for city in CITY_COORDS.keys():
        if city in text:
            return city
    return None

# ---------------- FRAUD PAYLOAD BUILDER ----------------
def build_fraud_payload(user_text: str, extracted: dict) -> dict:

    # ---------- Amount ----------
    amt = extracted.get("amt")
    if amt is None:
        amt = normalize_amount(user_text)

    if amt is None:
        st.error("❌ Could not extract transaction amount.")
        st.stop()

    # ---------- Time ----------
    time_hint = extracted.get("time_hint")
    if time_hint:
        trans_time = f"{datetime.now().date()} {time_hint}:00"
    else:
        trans_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------- City ----------
    city = extracted.get("merchant_city")

# Fallback: regex / keyword detection
    if not city:
        city = detect_city_from_text(user_text)

    if not city or city.lower() not in CITY_COORDS:
        st.error("❌ Could not determine merchant city from message.")
        st.stop()

    merch_lat, merch_long = CITY_COORDS[city.lower()]

    return {
        "trans_date_trans_time": trans_time,
        "cc_num": 0,
        "merchant": "Unknown Merchant",
        "category": "shopping",
        "amt": float(amt),
        "first": "N/A",
        "last": "N/A",
        "gender": "M",
        "street": "N/A",
        "city": USER_PROFILE["city"],
        "state": USER_PROFILE["state"],
        "zip": USER_PROFILE["zip"],
        "lat": USER_PROFILE["lat"],
        "long": USER_PROFILE["long"],
        "city_pop": USER_PROFILE["city_pop"],
        "job": USER_PROFILE["job"],
        "dob": USER_PROFILE["dob"],
        "trans_num": "AUTO",
        "merch_lat": merch_lat,
        "merch_long": merch_long
    }


# ---------------- SPENDING EXTRACTION ----------------
def extract_spending_info(user_text: str) -> dict:
    prompt = f"""
Extract monthly financial information.
Return JSON ONLY.

Fields:
- income
- housing
- food
- transport
- utilities
- discretionary

Text:
\"\"\"{user_text}\"\"\"
"""
    resp = llm.invoke(prompt)
    try:
        return json.loads(resp.content)
    except Exception:
        return {}


def build_spending_payload(extracted: dict) -> dict:
    income = extracted.get("income") or USER_PROFILE["monthly_income"]

    housing = extracted.get("housing", 0)
    food = extracted.get("food", 0)
    transport = extracted.get("transport", 0)
    utilities = extracted.get("utilities", 0)
    discretionary = extracted.get("discretionary", 0)

    total_spend = housing + food + transport + utilities + discretionary
    savings = max(income - total_spend, 0)

    def r(x): return round(x / income, 3) if income > 0 else 0

    return {
        "age": USER_PROFILE["age"],
        "household_size": USER_PROFILE["household_size"],
        "monthly_income": income,
        "housing_ratio": r(housing),
        "food_ratio": r(food),
        "transport_ratio": r(transport),
        "utilities_ratio": r(utilities),
        "discretionary_ratio": r(discretionary),
        "savings_ratio": r(savings),
        "owns_house": USER_PROFILE["owns_house"],
        "owns_vehicle": USER_PROFILE["owns_vehicle"],
        "city_type": USER_PROFILE["city_type"]
    }


# =====================================================
# CHAT LOOP
# =====================================================
user_input = st.chat_input("Ask about fraud, credit, or spending...")

if user_input:
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):

            intent = detect_intent(user_input)
            st.write("🧠 Detected intent:", intent)

            # ================= FRAUD =================
            if intent == "fraud":
                extracted = extract_transaction_info(user_input)
                payload = build_fraud_payload(user_input, extracted)

                st.write("🧾 Fraud payload:")
                st.json(payload)

                result = requests.post(
                    f"{API_BASE_URL}/fraud/detect",
                    json=payload
                ).json()

                st.success("🚨 Fraud Detection Result")
                st.json(result)

            # ================= SPENDING =================
            elif intent == "spending":
                extracted = extract_spending_info(user_input)
                payload = build_spending_payload(extracted)

                st.write("🧾 Spending payload:")
                st.json(payload)

                result = requests.post(
                    f"{API_BASE_URL}/spending-lite/predict",
                    json=payload
                ).json()

                st.success("📊 Spending Profile")
                st.json(result)

            # ================= CREDIT =================
            elif intent == "credit":
                st.info("Credit model integration already working (as tested earlier).")

            else:
                st.warning("❓ I couldn't determine what you want to analyze.")

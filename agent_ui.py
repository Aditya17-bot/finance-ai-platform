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
<<<<<<< HEAD
# MODE SELECTOR
# =====================================================
st.sidebar.header("Mode")
mode = st.sidebar.selectbox(
    "Choose how you want to run the models",
    ["Chat", "Fraud Manual", "Spending Manual", "Credit Manual"],
    index=0
)


# =====================================================
=======
>>>>>>> 359b44f4dadf28adc9965a9e66917e98d74a1a38
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

<<<<<<< HEAD
    return try_parse_json(resp.content)
=======
    try:
        return json.loads(resp.content)
    except Exception:
        return {}
>>>>>>> 359b44f4dadf28adc9965a9e66917e98d74a1a38

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
<<<<<<< HEAD
    if not time_hint:
        m = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", user_text)
        if m:
            time_hint = m.group(0)
=======
>>>>>>> 359b44f4dadf28adc9965a9e66917e98d74a1a38
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
<<<<<<< HEAD
    # 1) If user pasted JSON, parse it directly.
    direct = try_parse_json(user_text)
    if direct:
        return direct

    # 2) LLM extraction as fallback.
=======
>>>>>>> 359b44f4dadf28adc9965a9e66917e98d74a1a38
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
<<<<<<< HEAD
    parsed = try_parse_json(resp.content)
    if parsed:
        return parsed

    # 3) Regex fallback for patterns like "income 60000, housing 20000, ..."
    patterns = {
        "income": r"(income|monthly income)\s*(is|=)?\s*[\$₹]?\s*([\d,]+)",
        "housing": r"(housing|rent|mortgage)\s*(is|=)?\s*[\$₹]?\s*([\d,]+)",
        "food": r"(food|groceries)\s*(is|=)?\s*[\$₹]?\s*([\d,]+)",
        "transport": r"(transport|transportation|travel)\s*(is|=)?\s*[\$₹]?\s*([\d,]+)",
        "utilities": r"(utilities|utility)\s*(is|=)?\s*[\$₹]?\s*([\d,]+)",
        "discretionary": r"(discretionary|shopping|entertainment|misc)\s*(is|=)?\s*[\$₹]?\s*([\d,]+)"
    }
    extracted = {}
    for key, pat in patterns.items():
        m = re.search(pat, user_text, flags=re.IGNORECASE)
        if m:
            extracted[key] = float(m.group(3).replace(",", ""))

    return extracted

def try_parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group(0))
    except Exception:
        return {}
    return {}

def extract_credit_info(user_text: str) -> dict:
    prompt = f"""
Extract credit features for risk prediction.
Return JSON ONLY with ALL fields. If not mentioned, use null.

Fields:
- ExternalRiskEstimate
- MSinceOldestTradeOpen
- MSinceMostRecentTradeOpen
- AverageMInFile
- NumSatisfactoryTrades
- NumTrades60Ever2DerogPubRec
- NumTrades90Ever2DerogPubRec
- PercentTradesNeverDelq
- MSinceMostRecentDelq
- MaxDelq2PublicRecLast12M
- MaxDelqEver
- NumTotalTrades
- NumTradesOpeninLast12M
- PercentInstallTrades
- MSinceMostRecentInqexcl7days
- NumInqLast6M
- NumInqLast6Mexcl7days
- NetFractionRevolvingBurden
- NetFractionInstallBurden
- NumRevolvingTradesWBalance
- NumInstallTradesWBalance
- NumBank2NatlTradesWHighUtilization
- PercentTradesWBalance

Text:
\"\"\"{user_text}\"\"\"
"""
    resp = llm.invoke(prompt)
=======
>>>>>>> 359b44f4dadf28adc9965a9e66917e98d74a1a38
    try:
        return json.loads(resp.content)
    except Exception:
        return {}

<<<<<<< HEAD
def validate_credit_payload(payload: dict) -> list:
    required = [
        "ExternalRiskEstimate",
        "MSinceOldestTradeOpen",
        "MSinceMostRecentTradeOpen",
        "AverageMInFile",
        "NumSatisfactoryTrades",
        "NumTrades60Ever2DerogPubRec",
        "NumTrades90Ever2DerogPubRec",
        "PercentTradesNeverDelq",
        "MSinceMostRecentDelq",
        "MaxDelq2PublicRecLast12M",
        "MaxDelqEver",
        "NumTotalTrades",
        "NumTradesOpeninLast12M",
        "PercentInstallTrades",
        "MSinceMostRecentInqexcl7days",
        "NumInqLast6M",
        "NumInqLast6Mexcl7days",
        "NetFractionRevolvingBurden",
        "NetFractionInstallBurden",
        "NumRevolvingTradesWBalance",
        "NumInstallTradesWBalance",
        "NumBank2NatlTradesWHighUtilization",
        "PercentTradesWBalance"
    ]
    missing = [k for k in required if payload.get(k) is None]
    return missing

=======
>>>>>>> 359b44f4dadf28adc9965a9e66917e98d74a1a38

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
<<<<<<< HEAD
if mode == "Chat":
    user_input = st.chat_input("Ask about fraud, credit, or spending...")

    if user_input:
        st.chat_message("user").markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):

                intent = detect_intent(user_input)
                st.write("Spending Profile Detected intent:", intent)

                # ================= FRAUD =================
                if intent == "fraud":
                    extracted = extract_transaction_info(user_input)
                    payload = build_fraud_payload(user_input, extracted)

                    st.write("Spending Profile Fraud payload:")
                    st.caption("Note: `city/state/zip` are cardholder profile; merchant location is in `merch_lat/merch_long`.")
                    display_payload = dict(payload)
                    display_payload["merchant_city_detected"] = detect_city_from_text(user_input)
                    display_payload["time_hint_detected"] = extracted.get("time_hint")
                    st.json(display_payload)

                    result = requests.post(
                        f"{API_BASE_URL}/fraud/detect",
                        json=payload
                    ).json()

                    st.success("Spending Profile Fraud Detection Result")
                    st.json(result)

                # ================= SPENDING =================
                elif intent == "spending":
                    extracted = extract_spending_info(user_input)
                    payload = build_spending_payload(extracted)

                    st.write("Spending Profile Spending payload:")
                    st.json(payload)

                    result = requests.post(
                        f"{API_BASE_URL}/spending-lite/predict",
                        json=payload
                    ).json()

                    st.success("Spending Profile Spending Profile")
                    st.json(result)

                # ================= CREDIT =================
                elif intent == "credit":
                    payload = try_parse_json(user_input)
                    if not payload:
                        payload = extract_credit_info(user_input)

                    missing = validate_credit_payload(payload)
                    if missing:
                        st.warning("Spending Profile?? Credit prediction needs structured inputs.")
                        st.write("Missing fields:", missing)
                        st.info("Tip: paste a JSON object with all required fields.")
                        st.json({k: None for k in missing})
                        st.stop()

                    result = requests.post(
                        f"{API_BASE_URL}/credit-score/predict",
                        json=payload
                    ).json()

                    st.success("Error Credit Risk Result")
                    st.json(result)

                else:
                    st.warning("Error I couldn't determine what you want to analyze.")

# =====================================================
# MANUAL FORMS
# =====================================================
if mode == "Credit Manual":
    st.subheader("Credit Risk Form")
    st.caption("Fill the fields below to run the credit risk model without JSON.")

    SAMPLE_CREDIT_PROFILE = {
        "ExternalRiskEstimate": 72,
        "MSinceOldestTradeOpen": 180,
        "MSinceMostRecentTradeOpen": 6,
        "AverageMInFile": 84,
        "NumSatisfactoryTrades": 12,
        "NumTrades60Ever2DerogPubRec": 0,
        "NumTrades90Ever2DerogPubRec": 0,
        "PercentTradesNeverDelq": 96,
        "MSinceMostRecentDelq": 72,
        "MaxDelq2PublicRecLast12M": 7,
        "MaxDelqEver": 8,
        "NumTotalTrades": 15,
        "NumTradesOpeninLast12M": 3,
        "PercentInstallTrades": 33,
        "MSinceMostRecentInqexcl7days": 2,
        "NumInqLast6M": 1,
        "NumInqLast6Mexcl7days": 1,
        "NetFractionRevolvingBurden": 28,
        "NetFractionInstallBurden": 12,
        "NumRevolvingTradesWBalance": 4,
        "NumInstallTradesWBalance": 2,
        "NumBank2NatlTradesWHighUtilization": 1,
        "PercentTradesWBalance": 45
    }

    use_sample = st.checkbox("Use sample credit profile", value=True)

    with st.form("credit_form"):
        defaults = SAMPLE_CREDIT_PROFILE if use_sample else {k: 0 for k in SAMPLE_CREDIT_PROFILE}

        ExternalRiskEstimate = st.number_input("ExternalRiskEstimate", value=float(defaults["ExternalRiskEstimate"]))
        MSinceOldestTradeOpen = st.number_input("MSinceOldestTradeOpen", value=float(defaults["MSinceOldestTradeOpen"]))
        MSinceMostRecentTradeOpen = st.number_input("MSinceMostRecentTradeOpen", value=float(defaults["MSinceMostRecentTradeOpen"]))
        AverageMInFile = st.number_input("AverageMInFile", value=float(defaults["AverageMInFile"]))
        NumSatisfactoryTrades = st.number_input("NumSatisfactoryTrades", value=float(defaults["NumSatisfactoryTrades"]))
        NumTrades60Ever2DerogPubRec = st.number_input("NumTrades60Ever2DerogPubRec", value=float(defaults["NumTrades60Ever2DerogPubRec"]))
        NumTrades90Ever2DerogPubRec = st.number_input("NumTrades90Ever2DerogPubRec", value=float(defaults["NumTrades90Ever2DerogPubRec"]))
        PercentTradesNeverDelq = st.number_input("PercentTradesNeverDelq", value=float(defaults["PercentTradesNeverDelq"]))
        MSinceMostRecentDelq = st.number_input("MSinceMostRecentDelq", value=float(defaults["MSinceMostRecentDelq"]))
        MaxDelq2PublicRecLast12M = st.number_input("MaxDelq2PublicRecLast12M", value=float(defaults["MaxDelq2PublicRecLast12M"]))
        MaxDelqEver = st.number_input("MaxDelqEver", value=float(defaults["MaxDelqEver"]))
        NumTotalTrades = st.number_input("NumTotalTrades", value=float(defaults["NumTotalTrades"]))
        NumTradesOpeninLast12M = st.number_input("NumTradesOpeninLast12M", value=float(defaults["NumTradesOpeninLast12M"]))
        PercentInstallTrades = st.number_input("PercentInstallTrades", value=float(defaults["PercentInstallTrades"]))
        MSinceMostRecentInqexcl7days = st.number_input("MSinceMostRecentInqexcl7days", value=float(defaults["MSinceMostRecentInqexcl7days"]))
        NumInqLast6M = st.number_input("NumInqLast6M", value=float(defaults["NumInqLast6M"]))
        NumInqLast6Mexcl7days = st.number_input("NumInqLast6Mexcl7days", value=float(defaults["NumInqLast6Mexcl7days"]))
        NetFractionRevolvingBurden = st.number_input("NetFractionRevolvingBurden", value=float(defaults["NetFractionRevolvingBurden"]))
        NetFractionInstallBurden = st.number_input("NetFractionInstallBurden", value=float(defaults["NetFractionInstallBurden"]))
        NumRevolvingTradesWBalance = st.number_input("NumRevolvingTradesWBalance", value=float(defaults["NumRevolvingTradesWBalance"]))
        NumInstallTradesWBalance = st.number_input("NumInstallTradesWBalance", value=float(defaults["NumInstallTradesWBalance"]))
        NumBank2NatlTradesWHighUtilization = st.number_input("NumBank2NatlTradesWHighUtilization", value=float(defaults["NumBank2NatlTradesWHighUtilization"]))
        PercentTradesWBalance = st.number_input("PercentTradesWBalance", value=float(defaults["PercentTradesWBalance"]))

        submitted = st.form_submit_button("Run Credit Risk")

        if submitted:
            payload = {
                "ExternalRiskEstimate": ExternalRiskEstimate,
                "MSinceOldestTradeOpen": MSinceOldestTradeOpen,
                "MSinceMostRecentTradeOpen": MSinceMostRecentTradeOpen,
                "AverageMInFile": AverageMInFile,
                "NumSatisfactoryTrades": NumSatisfactoryTrades,
                "NumTrades60Ever2DerogPubRec": NumTrades60Ever2DerogPubRec,
                "NumTrades90Ever2DerogPubRec": NumTrades90Ever2DerogPubRec,
                "PercentTradesNeverDelq": PercentTradesNeverDelq,
                "MSinceMostRecentDelq": MSinceMostRecentDelq,
                "MaxDelq2PublicRecLast12M": MaxDelq2PublicRecLast12M,
                "MaxDelqEver": MaxDelqEver,
                "NumTotalTrades": NumTotalTrades,
                "NumTradesOpeninLast12M": NumTradesOpeninLast12M,
                "PercentInstallTrades": PercentInstallTrades,
                "MSinceMostRecentInqexcl7days": MSinceMostRecentInqexcl7days,
                "NumInqLast6M": NumInqLast6M,
                "NumInqLast6Mexcl7days": NumInqLast6Mexcl7days,
                "NetFractionRevolvingBurden": NetFractionRevolvingBurden,
                "NetFractionInstallBurden": NetFractionInstallBurden,
                "NumRevolvingTradesWBalance": NumRevolvingTradesWBalance,
                "NumInstallTradesWBalance": NumInstallTradesWBalance,
                "NumBank2NatlTradesWHighUtilization": NumBank2NatlTradesWHighUtilization,
                "PercentTradesWBalance": PercentTradesWBalance
            }

            result = requests.post(
                f"{API_BASE_URL}/credit-score/predict",
                json=payload
            ).json()

            st.success("Error Credit Risk Result")
            st.json(result)

if mode == "Spending Manual":
    st.subheader("Spending Classifier Form")
    st.caption("Defaults are prefilled from a typical monthly profile.")

    with st.form("spending_form"):
        income = st.number_input("Monthly Income", value=60000.0)
        housing = st.number_input("Housing", value=20000.0)
        food = st.number_input("Food", value=8000.0)
        transport = st.number_input("Transport", value=3000.0)
        utilities = st.number_input("Utilities", value=2000.0)
        discretionary = st.number_input("Discretionary", value=4000.0)

        submitted = st.form_submit_button("Run Spending Classifier")
        if submitted:
            extracted = {
                "income": income,
                "housing": housing,
                "food": food,
                "transport": transport,
                "utilities": utilities,
                "discretionary": discretionary
            }
            payload = build_spending_payload(extracted)
            st.json(payload)
            result = requests.post(
                f"{API_BASE_URL}/spending-lite/predict",
                json=payload
            ).json()
            st.success("Spending Profile Spending Profile")
            st.json(result)

if mode == "Fraud Manual":
    st.subheader("Fraud Detection Form")
    st.caption("Cardholder profile is fixed; set merchant city, amount, and time.")

    with st.form("fraud_form"):
        amt = st.number_input("Transaction Amount", value=2300.0)
        merchant_city = st.selectbox("Merchant City", list(CITY_COORDS.keys()), index=1)
        time_hint = st.text_input("Time (HH:MM, 24-hour)", value="14:30")

        submitted = st.form_submit_button("Run Fraud Detection")
        if submitted:
            extracted = {
                "amt": amt,
                "merchant_city": merchant_city,
                "time_hint": time_hint
            }
            payload = build_fraud_payload("", extracted)
            st.json(payload)
            result = requests.post(
                f"{API_BASE_URL}/fraud/detect",
                json=payload
            ).json()
            st.success("Spending Profile Fraud Detection Result")
            st.json(result)
=======
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
>>>>>>> 359b44f4dadf28adc9965a9e66917e98d74a1a38

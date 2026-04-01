from pydantic import BaseModel, Field, validator
from typing import Literal, List, Optional
from datetime import datetime


# =====================================================
# CREDIT INPUT — HELOC Dataset Schema
# =====================================================
class CreditInput(BaseModel):
    ExternalRiskEstimate: float = Field(..., ge=0, le=100, example=70, description="External credit risk score (0-100)")
    MSinceOldestTradeOpen: float = Field(..., ge=0, example=120, description="Months since oldest trade opened")
    MSinceMostRecentTradeOpen: float = Field(..., ge=0, example=6, description="Months since most recent trade opened")
    AverageMInFile: float = Field(..., ge=0, example=72, description="Average months in file")
    NumSatisfactoryTrades: float = Field(..., ge=0, example=15, description="Number of satisfactory trades")
    NumTrades60Ever2DerogPubRec: float = Field(..., ge=0, example=1, description="Trades 60+ days delinquent")
    NumTrades90Ever2DerogPubRec: float = Field(..., ge=0, example=0, description="Trades 90+ days delinquent")
    PercentTradesNeverDelq: float = Field(..., ge=0, le=100, example=90, description="% trades never delinquent")
    MSinceMostRecentDelq: float = Field(..., ge=0, example=30, description="Months since most recent delinquency")
    MaxDelq2PublicRecLast12M: float = Field(..., ge=0, example=2, description="Max delinquency in last 12M")
    MaxDelqEver: float = Field(..., ge=0, example=4, description="Max delinquency ever")
    NumTotalTrades: float = Field(..., ge=0, example=20, description="Total number of trades")
    NumTradesOpeninLast12M: float = Field(..., ge=0, example=3, description="Trades opened in last 12M")
    PercentInstallTrades: float = Field(..., ge=0, le=100, example=40, description="% installment trades")
    MSinceMostRecentInqexcl7days: float = Field(..., ge=0, example=5, description="Months since recent inquiry (excl. 7 days)")
    NumInqLast6M: float = Field(..., ge=0, example=2, description="Inquiries in last 6 months")
    NumInqLast6Mexcl7days: float = Field(..., ge=0, example=2, description="Inquiries last 6M (excl. 7 days)")
    NetFractionRevolvingBurden: float = Field(..., ge=0, example=45, description="Net fraction revolving burden")
    NetFractionInstallBurden: float = Field(..., ge=0, example=60, description="Net fraction install burden")
    NumRevolvingTradesWBalance: float = Field(..., ge=0, example=5, description="Revolving trades with balance")
    NumInstallTradesWBalance: float = Field(..., ge=0, example=3, description="Install trades with balance")
    NumBank2NatlTradesWHighUtilization: float = Field(..., ge=0, example=2, description="High utilization trades")
    PercentTradesWBalance: float = Field(..., ge=0, le=100, example=65, description="% trades with balance")

    class Config:
        json_schema_extra = {
            "example": {
                "ExternalRiskEstimate": 70,
                "MSinceOldestTradeOpen": 120,
                "MSinceMostRecentTradeOpen": 6,
                "AverageMInFile": 72,
                "NumSatisfactoryTrades": 15,
                "NumTrades60Ever2DerogPubRec": 1,
                "NumTrades90Ever2DerogPubRec": 0,
                "PercentTradesNeverDelq": 90,
                "MSinceMostRecentDelq": 30,
                "MaxDelq2PublicRecLast12M": 2,
                "MaxDelqEver": 4,
                "NumTotalTrades": 20,
                "NumTradesOpeninLast12M": 3,
                "PercentInstallTrades": 40,
                "MSinceMostRecentInqexcl7days": 5,
                "NumInqLast6M": 2,
                "NumInqLast6Mexcl7days": 2,
                "NetFractionRevolvingBurden": 45,
                "NetFractionInstallBurden": 60,
                "NumRevolvingTradesWBalance": 5,
                "NumInstallTradesWBalance": 3,
                "NumBank2NatlTradesWHighUtilization": 2,
                "PercentTradesWBalance": 65
            }
        }


# =====================================================
# SPENDING LITE INPUT
# =====================================================
class SpendingLiteInput(BaseModel):
    age: int = Field(..., ge=18, le=100, example=30)
    household_size: int = Field(..., ge=1, le=20, example=3)
    monthly_income: float = Field(..., ge=0, example=80000)

    housing_ratio: float = Field(..., ge=0, le=1, example=0.35)
    food_ratio: float = Field(..., ge=0, le=1, example=0.20)
    transport_ratio: float = Field(..., ge=0, le=1, example=0.10)
    utilities_ratio: float = Field(..., ge=0, le=1, example=0.07)
    discretionary_ratio: float = Field(..., ge=0, le=1, example=0.25)
    savings_ratio: float = Field(..., ge=0, le=1, example=0.15)

    owns_house: int = Field(..., example=1, description="1 = Yes, 0 = No")
    owns_vehicle: int = Field(..., example=1, description="1 = Yes, 0 = No")

    city_type: Literal["urban", "semi-urban", "rural"] = Field(..., example="urban")

    @validator("housing_ratio", "food_ratio", "transport_ratio", "utilities_ratio", "discretionary_ratio", "savings_ratio")
    def ratio_must_be_valid(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Ratio must be between 0.0 and 1.0")
        return round(v, 4)


# =====================================================
# FRAUD INPUT — Credit Card Transactions Schema
# =====================================================
class FraudInput(BaseModel):
    trans_date_trans_time: str = Field(..., example="2024-01-15 14:32:00")
    cc_num: float = Field(..., example=4532015112830366)
    merchant: str = Field(..., example="fraud_Kirlin and Sons")
    category: str = Field(..., example="grocery_pos")
    amt: float = Field(..., ge=0, example=149.62)
    first: str = Field(..., example="Jennifer")
    last: str = Field(..., example="Banks")
    gender: Literal["M", "F"] = Field(..., example="F")
    street: str = Field(..., example="561 Perry Cove")
    city: str = Field(..., example="Moravian Falls")
    state: str = Field(..., example="NC")
    zip_code: int = Field(..., alias="zip", example=28654)
    lat: float = Field(..., example=36.0788)
    long: float = Field(..., example=-81.1781)
    city_pop: int = Field(..., example=3495)
    job: str = Field(..., example="Psychologist, counselling")
    dob: str = Field(..., example="1988-03-09")
    trans_num: str = Field(..., example="2da90c7d74bd46a0caf3777415b3ebd3")
    merch_lat: float = Field(..., example=36.011293)
    merch_long: float = Field(..., example=-82.048315)

    class Config:
        populate_by_name = True


# =====================================================
# AGENT TRANSACTION SCHEMA
# =====================================================
class Transaction(BaseModel):
    amount: float = Field(..., ge=0, example=1200.0)
    category: Literal["Food", "Rent", "Luxury", "Investment", "Misc"]
    hour: int = Field(..., ge=0, le=23, example=14)
    location_change: int = Field(..., ge=0, le=1, example=0, description="1 = location changed, 0 = same")
    merchant_type: int = Field(..., ge=0, le=10, example=1)
    txn_velocity: int = Field(..., ge=1, le=20, example=2, description="Transactions per hour")


# =====================================================
# AGENT INPUT
# =====================================================
class AgentInput(BaseModel):
    credit_limit: float = Field(100000, ge=1000, example=100000)
    transactions: List[Transaction] = Field(..., min_items=1)

    class Config:
        json_schema_extra = {
            "example": {
                "credit_limit": 100000,
                "transactions": [
                    {"amount": 1200, "category": "Food", "hour": 20, "location_change": 0, "merchant_type": 1, "txn_velocity": 1},
                    {"amount": 5000, "category": "Luxury", "hour": 18, "location_change": 0, "merchant_type": 2, "txn_velocity": 2},
                    {"amount": 15000, "category": "Rent", "hour": 10, "location_change": 0, "merchant_type": 0, "txn_velocity": 1}
                ]
            }
        }


# =====================================================
# RESPONSE SCHEMAS
# =====================================================
class FraudResponse(BaseModel):
    status: str
    confidence: Optional[float] = None
    risk_level: str
    flagged_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SpendingResponse(BaseModel):
    spending_type: str
    category_breakdown: Optional[dict] = None


class CreditResponse(BaseModel):
    credit_score: int
    risk_band: str
    recommendation: str


class AgentInsight(BaseModel):
    type: Literal["warning", "info", "success", "danger"]
    message: str
    priority: int = Field(1, ge=1, le=5)


class AgentResponse(BaseModel):
    spending_type: str
    credit_score: int
    fraud_status: str
    insights: List[str]
    risk_summary: Optional[str] = None
    analyzed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
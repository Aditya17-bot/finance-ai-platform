from pydantic import BaseModel, Field
from typing import Literal

# --- CREDIT INPUT ---
class CreditInput(BaseModel):
    ExternalRiskEstimate: float
    MSinceOldestTradeOpen: float
    MSinceMostRecentTradeOpen: float
    AverageMInFile: float
    NumSatisfactoryTrades: float
    NumTrades60Ever2DerogPubRec: float
    NumTrades90Ever2DerogPubRec: float
    PercentTradesNeverDelq: float
    MSinceMostRecentDelq: float
    MaxDelq2PublicRecLast12M: float
    MaxDelqEver: float
    NumTotalTrades: float
    NumTradesOpeninLast12M: float
    PercentInstallTrades: float
    MSinceMostRecentInqexcl7days: float
    NumInqLast6M: float
    NumInqLast6Mexcl7days: float
    NetFractionRevolvingBurden: float
    NetFractionInstallBurden: float
    NumRevolvingTradesWBalance: float
    NumInstallTradesWBalance: float
    NumBank2NatlTradesWHighUtilization: float
    PercentTradesWBalance: float

class SpendingLiteInput(BaseModel):
    age: int = Field(..., example=30)
    household_size: int = Field(..., example=3)
    monthly_income: float = Field(..., example=80000)

    housing_ratio: float = Field(..., example=0.35)
    food_ratio: float = Field(..., example=0.2)
    transport_ratio: float = Field(..., example=0.1)
    utilities_ratio: float = Field(..., example=0.07)
    discretionary_ratio: float = Field(..., example=0.25)
    savings_ratio: float = Field(..., example=0.15)

    owns_house: int = Field(..., example=1, description="1 = Yes, 0 = No")
    owns_vehicle: int = Field(..., example=1, description="1 = Yes, 0 = No")

    city_type: Literal["urban", "semi-urban", "rural"] = Field(
        ..., example="urban"
    )    


class FraudInput(BaseModel):
    trans_date_trans_time: str
    cc_num: float
    merchant: str
    category: str
    amt: float
    first: str
    last: str
    gender: str
    street: str
    city: str
    state: str
    zip_code: int = Field(alias="zip")
    lat: float
    long: float
    city_pop: int
    job: str
    dob: str
    trans_num: str
    merch_lat: float
    merch_long: float

    class Config:
        populate_by_name = True
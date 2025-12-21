from pydantic import BaseModel, Field

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

# --- SPENDING INPUT ---
class SpendingInput(BaseModel):
    Household_Head_Sex: str = Field(alias="Household Head Sex")
    Household_Head_Age: float = Field(alias="Household Head Age")
    Household_Head_Marital_Status: str = Field(alias="Household Head Marital Status")
    Household_Head_Highest_Grade_Completed: str = Field(alias="Household Head Highest Grade Completed")
    Household_Head_Job_or_Business_Indicator: str = Field(alias="Household Head Job or Business Indicator")
    Household_Head_Occupation: str = Field(alias="Household Head Occupation")
    Household_Head_Class_of_Worker: str = Field(alias="Household Head Class of Worker")
    Type_of_Household: str = Field(alias="Type of Household")
    Total_Number_of_Family_members: float = Field(alias="Total Number of Family members")
    Members_with_age_less_than_5_year_old: float = Field(alias="Members with age less than 5 year old")
    Members_with_age_5_17_years_old: float = Field(alias="Members with age 5 - 17 years old")
    Total_number_of_family_members_employed: float = Field(alias="Total number of family members employed")
    Total_Food_Expenditure_x: float = Field(alias="Total Food Expenditure_x")
    Bread_and_Cereals_Expenditure_x: float = Field(alias="Bread and Cereals Expenditure_x")
    Total_Rice_Expenditure_x: float = Field(alias="Total Rice Expenditure_x")
    Meat_Expenditure_x: float = Field(alias="Meat Expenditure_x")
    Total_Fish_and_marine_products_Expenditure_x: float = Field(alias="Total Fish and  marine products Expenditure_x")
    Fruit_Expenditure_x: float = Field(alias="Fruit Expenditure_x")
    Vegetables_Expenditure_x: float = Field(alias="Vegetables Expenditure_x")
    Restaurant_and_hotels_Expenditure_x: float = Field(alias="Restaurant and hotels Expenditure_x")
    Alcoholic_Beverages_Expenditure_x: float = Field(alias="Alcoholic Beverages Expenditure_x")
    Tobacco_Expenditure_x: float = Field(alias="Tobacco Expenditure_x")
    Clothing_Footwear_and_Other_Wear_Expenditure_x: float = Field(alias="Clothing, Footwear and Other Wear Expenditure_x")
    Housing_and_water_Expenditure_x: float = Field(alias="Housing and water Expenditure_x")
    Medical_Care_Expenditure_x: float = Field(alias="Medical Care Expenditure_x")
    Transportation_Expenditure_x: float = Field(alias="Transportation Expenditure_x")
    Communication_Expenditure_x: float = Field(alias="Communication Expenditure_x")
    Education_Expenditure_x: float = Field(alias="Education Expenditure_x")
    Miscellaneous_Goods_and_Services_Expenditure_x: float = Field(alias="Miscellaneous Goods and Services Expenditure_x")
    Special_Occasions_Expenditure_x: float = Field(alias="Special Occasions Expenditure_x")
    Main_Source_of_Income: str = Field(alias="Main Source of Income")
    Number_of_Airconditioner: float = Field(alias="Number of Airconditioner")
    Electricity: float = Field(alias="Electricity")
    House_Age: float = Field(alias="House Age")
    Number_of_bedrooms: float = Field(alias="Number of bedrooms")
    Number_of_Personal_Computer: float = Field(alias="Number of Personal Computer")
    Total_Income_from_Entrepreneurial_Acitivites: float = Field(alias="Total Income from Entrepreneurial Acitivites")
    Total_Household_Income: float = Field(alias="Total Household Income")
    Number_of_Component_Stereo_set: float = Field(alias="Number of Component/Stereo set")
    Type_of_Roof: str = Field(alias="Type of Roof")
    Number_of_Washing_Machine: float = Field(alias="Number of Washing Machine")
    Number_of_Motorized_Banca: float = Field(alias="Number of Motorized Banca")
    Number_of_Cellular_phone: float = Field(alias="Number of Cellular phone")
    Number_of_Television: float = Field(alias="Number of Television")
    Imputed_House_Rental_Value: float = Field(alias="Imputed House Rental Value")
    Toilet_Facilities: str = Field(alias="Toilet Facilities")
    Type_of_Walls: str = Field(alias="Type of Walls")
    House_Floor_Area: float = Field(alias="House Floor Area")
    Agricultural_Household_indicator: float = Field(alias="Agricultural Household indicator")
    Type_of_Building_House: str = Field(alias="Type of Building/House")
    Number_of_Stove_with_Oven_Gas_Range: float = Field(alias="Number of Stove with Oven/Gas Range")
    Number_of_Refrigerator_Freezer: float = Field(alias="Number of Refrigerator/Freezer")
    Number_of_Car_Jeep_Van: float = Field(alias="Number of Car, Jeep, Van")
    Number_of_Landline_wireless_telephones: float = Field(alias="Number of Landline/wireless telephones")
    Number_of_Motorcycle_Tricycle: float = Field(alias="Number of Motorcycle/Tricycle")
    Region: str = Field(alias="Region")
    Crop_Farming_and_Gardening_expenses: float = Field(alias="Crop Farming and Gardening expenses")
    Main_Source_of_Water_Supply: str = Field(alias="Main Source of Water Supply")
    Tenure_Status: str = Field(alias="Tenure Status")
    Number_of_CD_VCD_DVD: float = Field(alias="Number of CD/VCD/DVD")
    Total_Food_Expenditure_y: float = Field(alias="Total Food Expenditure_y")
    Bread_and_Cereals_Expenditure_y: float = Field(alias="Bread and Cereals Expenditure_y")
    Total_Rice_Expenditure_y: float = Field(alias="Total Rice Expenditure_y")
    Meat_Expenditure_y: float = Field(alias="Meat Expenditure_y")
    Total_Fish_and_marine_products_Expenditure_y: float = Field(alias="Total Fish and  marine products Expenditure_y")
    Fruit_Expenditure_y: float = Field(alias="Fruit Expenditure_y")
    Vegetables_Expenditure_y: float = Field(alias="Vegetables Expenditure_y")
    Restaurant_and_hotels_Expenditure_y: float = Field(alias="Restaurant and hotels Expenditure_y")
    Alcoholic_Beverages_Expenditure_y: float = Field(alias="Alcoholic Beverages Expenditure_y")
    Tobacco_Expenditure_y: float = Field(alias="Tobacco Expenditure_y")
    Clothing_Footwear_and_Other_Wear_Expenditure_y: float = Field(alias="Clothing, Footwear and Other Wear Expenditure_y")
    Housing_and_water_Expenditure_y: float = Field(alias="Housing and water Expenditure_y")
    Medical_Care_Expenditure_y: float = Field(alias="Medical Care Expenditure_y")
    Transportation_Expenditure_y: float = Field(alias="Transportation Expenditure_y")
    Communication_Expenditure_y: float = Field(alias="Communication Expenditure_y")
    Education_Expenditure_y: float = Field(alias="Education Expenditure_y")
    Miscellaneous_Goods_and_Services_Expenditure_y: float = Field(alias="Miscellaneous Goods and Services Expenditure_y")
    Special_Occasions_Expenditure_y: float = Field(alias="Special Occasions Expenditure_y")

    class Config:
        populate_by_name = True

# --- FRAUD INPUT ---
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
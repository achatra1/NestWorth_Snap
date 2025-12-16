"""Financial profile model for user data storage."""
from pydantic import BaseModel, Field, BeforeValidator, field_validator
from typing import Annotated, Optional, Literal
from datetime import datetime, timezone, date
from bson import ObjectId


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class LeaveDetails(BaseModel):
    """Parental leave details."""
    duration_weeks: int = Field(ge=0, alias="durationWeeks")
    percent_paid: int = Field(ge=0, le=100, alias="percentPaid")
    
    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel
    }


class FinancialProfileBase(BaseModel):
    """Base financial profile fields."""
    partner1_income: float = Field(ge=0, alias="partner1Income")
    partner2_income: float = Field(ge=0, alias="partner2Income")
    zip_code: str = Field(min_length=5, max_length=5, alias="zipCode")
    due_date: date = Field(alias="dueDate")
    current_savings: float = Field(ge=0, alias="currentSavings")
    number_of_children: int = Field(default=1, ge=1, le=10, alias="numberOfChildren")
    childcare_preference: Literal["daycare", "nanny", "stay-at-home"] = Field(alias="childcarePreference")
    partner1_leave: LeaveDetails = Field(alias="partner1Leave")
    partner2_leave: LeaveDetails = Field(alias="partner2Leave")
    monthly_housing_cost: float = Field(ge=0, alias="monthlyHousingCost")
    monthly_credit_card_expenses: float = Field(default=0.0, ge=0, alias="monthlyCreditCardExpenses")
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Validate ZIP code is 5 digits."""
        if not v.isdigit():
            raise ValueError('ZIP code must contain only digits')
        if len(v) != 5:
            raise ValueError('ZIP code must be exactly 5 digits')
        return v
    
    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel
    }


class FinancialProfileCreate(FinancialProfileBase):
    """Schema for creating a financial profile."""
    pass


class FinancialProfile(FinancialProfileBase):
    """Complete financial profile with metadata."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(alias="userId")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "alias_generator": to_camel,
        "json_schema_extra": {
            "example": {
                "userId": "507f1f77bcf86cd799439011",
                "partner1Income": 5000.0,
                "partner2Income": 4500.0,
                "zipCode": "10001",
                "dueDate": "2026-04-15",
                "currentSavings": 10000.0,
                "numberOfChildren": 1,
                "childcarePreference": "daycare",
                "partner1Leave": {"durationWeeks": 12, "percentPaid": 100},
                "partner2Leave": {"durationWeeks": 12, "percentPaid": 60},
                "monthlyHousingCost": 2000.0,
                "monthlyCreditCardExpenses": 500.0,
                "createdAt": "2025-12-15T10:05:00Z",
                "updatedAt": "2025-12-15T10:05:00Z"
            }
        }
    }


class FinancialProfileResponse(BaseModel):
    """Schema for financial profile response."""
    id: str
    user_id: str = Field(alias="userId")
    partner1_income: float = Field(alias="partner1Income")
    partner2_income: float = Field(alias="partner2Income")
    zip_code: str = Field(alias="zipCode")
    due_date: str = Field(alias="dueDate")  # ISO date string for frontend
    current_savings: float = Field(alias="currentSavings")
    number_of_children: int = Field(alias="numberOfChildren")
    childcare_preference: str = Field(alias="childcarePreference")
    partner1_leave: LeaveDetails = Field(alias="partner1Leave")
    partner2_leave: LeaveDetails = Field(alias="partner2Leave")
    monthly_housing_cost: float = Field(alias="monthlyHousingCost")
    monthly_credit_card_expenses: float = Field(alias="monthlyCreditCardExpenses")
    created_at: str = Field(alias="createdAt")  # ISO datetime string
    updated_at: str = Field(alias="updatedAt")  # ISO datetime string
    
    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel,
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "userId": "507f1f77bcf86cd799439011",
                "partner1Income": 5000.0,
                "partner2Income": 4500.0,
                "zipCode": "10001",
                "dueDate": "2026-04-15",
                "currentSavings": 10000.0,
                "numberOfChildren": 1,
                "childcarePreference": "daycare",
                "partner1Leave": {"durationWeeks": 12, "percentPaid": 100},
                "partner2Leave": {"durationWeeks": 12, "percentPaid": 60},
                "monthlyHousingCost": 2000.0,
                "monthlyCreditCardExpenses": 500.0,
                "createdAt": "2025-12-15T10:05:00Z",
                "updatedAt": "2025-12-15T10:05:00Z"
            }
        }
    }
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TransactionCreate(BaseModel):
    description: str
    amount: float
    transaction_type: str
    category: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    description: str
    amount: float
    transaction_type: str
    category: Optional[str]
    date: datetime

    class Config:
        from_attributes = True

class ClientCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

    date_of_birth: Optional[str] = None
    occupation: Optional[str] = None
    city: Optional[str] = None

    monthly_income: float = 0
    other_income: float = 0

    monthly_budget: float = 0
    current_savings: float = 0

    existing_loan: float = 0
    monthly_emi: float = 0

    savings_goal: float = 0
    goal_type: Optional[str] = None

    target_amount: float = 0
    target_date: Optional[str] = None


class ClientResponse(ClientCreate):
    id: int

    class Config:
        from_attributes = True
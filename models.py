from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    category = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    date_of_birth = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    city = Column(String, nullable=True)

    monthly_income = Column(Float, default=0)
    other_income = Column(Float, default=0)

    monthly_budget = Column(Float, default=0)
    current_savings = Column(Float, default=0)

    existing_loan = Column(Float, default=0)
    monthly_emi = Column(Float, default=0)

    savings_goal = Column(Float, default=0)
    goal_type = Column(String, nullable=True)

    target_amount = Column(Float, default=0)
    target_date = Column(String, nullable=True)
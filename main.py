from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas

from database import engine, get_db
from ai_model import predict_category
from forecast import predict_expenses
from anomaly import detect_anomalies
from advisor import generate_financial_advice
from pydantic import BaseModel
from chatbot import ask_gemini
class ChatRequest(BaseModel):
    message: str

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Finance Controller",
    description="AI-powered financial management system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def home():
    return {
        "message": "AI Finance Controller API is running!",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# Add transaction
@app.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db)
):
    new_transaction = models.Transaction(
        description=transaction.description,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        category=transaction.category
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


# Get all transactions
@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()

    return transactions


# Get single transaction
@app.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction


# Delete transaction
@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }


# Financial summary
@app.get("/summary")
def financial_summary(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()

    total_income = sum(
        t.amount for t in transactions
        if t.transaction_type.lower() == "income"
    )

    total_expense = sum(
        t.amount for t in transactions
        if t.transaction_type.lower() == "expense"
    )

    balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }
@app.post("/predict-category")
def predict_expense_category(data: dict):
    description = data.get("description", "").strip()

    if not description:
        raise HTTPException(
            status_code=400,
            detail="Description is required"
        )

    result = predict_category(description)

    return result

@app.get("/forecast")
def get_forecast(
    days: int = 7,
    db: Session = Depends(get_db)
):

    if days < 1 or days > 30:
        raise HTTPException(
            status_code=400,
            detail="Forecast days must be between 1 and 30"
        )

    return predict_expenses(
        db=db,
        days=days
    )
@app.get("/anomalies")
def get_anomalies(
    db: Session = Depends(get_db)
):
   transactions = db.query(models.Transaction).all()
   return detect_anomalies(transactions)

@app.get("/advisor")
def financial_advisor(
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(models.Transaction)
        .all()
    )

    # Get forecast
    try:
        forecast_result = predict_expenses(
    db=db,
    days=7
)
    except Exception:
        forecast_result = {}

    # Get anomalies
    try:
        anomaly_result = detect_anomalies(
            transactions
        )
    except Exception:
        anomaly_result = {
            "anomalies_found": 0,
            "anomalies": []
        }

    # Generate financial advice
    advice = generate_financial_advice(
        transactions,
        forecast=forecast_result,
        anomalies=anomaly_result
    )

    return advice

@app.post("/chat")
def chat_with_financial_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        # Get client profile
        client = (
            db.query(models.Client)
            .first()
        )

        client_data = {}

        if client:
            client_data = {
                "full_name": client.full_name,
                "email": client.email,
                "phone": client.phone,
                "date_of_birth": client.date_of_birth,
                "occupation": client.occupation,
                "city": client.city,
                "monthly_income": client.monthly_income,
                "other_income": client.other_income,
                "monthly_budget": client.monthly_budget,
                "current_savings": client.current_savings,
                "existing_loan": client.existing_loan,
                "monthly_emi": client.monthly_emi,
                "savings_goal": client.savings_goal,
                "goal_type": client.goal_type,
                "target_amount": client.target_amount,
                "target_date": client.target_date,
            }

        # Get transactions
        transactions = (
            db.query(models.Transaction)
            .all()
        )

        transaction_data = [
            {
                "id": transaction.id,
                "description": transaction.description,
                "amount": float(transaction.amount),
                "transaction_type": transaction.transaction_type,
                "category": transaction.category,
                "date": str(transaction.date),
            }
            for transaction in transactions
        ]

        # Calculate summary
        total_income = sum(
            float(transaction.amount)
            for transaction in transactions
            if transaction.transaction_type.lower() == "income"
        )

        total_expense = sum(
            float(transaction.amount)
            for transaction in transactions
            if transaction.transaction_type.lower() == "expense"
        )

        summary_data = {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
        }

        # Forecast
        try:
            forecast_data = predict_expenses(
                db=db,
                days=7
            )
        except Exception:
            forecast_data = {}

        # Anomalies
        try:
            anomaly_data = detect_anomalies(
                transactions
            )
        except Exception:
            anomaly_data = {
                "total_transactions": 0,
                "anomalies_found": 0,
                "anomalies": [],
            }

        # Ask Gemini
        response = ask_gemini(
            message=request.message,
            client_data=client_data,
            transactions=transaction_data,
            summary=summary_data,
            forecast=forecast_data,
            anomalies=anomaly_data,
        )

        return {
            "status": "success",
            "message": response
        }

    except Exception as error:
        print("Chat error:", error)

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

# =========================
# CLIENT PROFILE
# =========================

@app.post("/client", response_model=schemas.ClientResponse)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db)
):
    new_client = models.Client(
        full_name=client.full_name,
        email=client.email,
        phone=client.phone,
        date_of_birth=client.date_of_birth,
        occupation=client.occupation,
        city=client.city,
        monthly_income=client.monthly_income,
        other_income=client.other_income,
        monthly_budget=client.monthly_budget,
        current_savings=client.current_savings,
        existing_loan=client.existing_loan,
        monthly_emi=client.monthly_emi,
        savings_goal=client.savings_goal,
        goal_type=client.goal_type,
        target_amount=client.target_amount,
        target_date=client.target_date
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client


@app.get("/client", response_model=list[schemas.ClientResponse])
def get_clients(
    db: Session = Depends(get_db)
):
    clients = db.query(models.Client).all()

    return clients
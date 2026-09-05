from datetime import datetime, timedelta

import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

import models


def calculate_balance(db: Session):
    transactions = db.query(models.Transaction).all()

    total_income = sum(
        float(t.amount)
        for t in transactions
        if t.transaction_type.lower() == "income"
    )

    total_expense = sum(
        float(t.amount)
        for t in transactions
        if t.transaction_type.lower() == "expense"
    )

    return total_income - total_expense


def predict_expenses(db: Session, days: int = 7):

    transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.transaction_type.ilike("expense")
        )
        .order_by(models.Transaction.date)
        .all()
    )

    current_balance = calculate_balance(db)

    # -----------------------------------------
    # NO EXPENSE DATA
    # -----------------------------------------

    if not transactions:
        return {
            "forecast_days": days,
            "average_daily_expense": 0,
            "predicted_total_expense": 0,
            "current_balance": round(current_balance, 2),
            "projected_balance": round(current_balance, 2),
            "model_used": "No expense data",
            "predictions": []
        }

    # -----------------------------------------
    # GROUP EXPENSES BY DATE
    # -----------------------------------------

    daily_expenses = {}

    for transaction in transactions:

        expense_date = transaction.date.date()

        daily_expenses.setdefault(
            expense_date,
            0
        )

        daily_expenses[expense_date] += float(
            transaction.amount
        )

    dates = sorted(daily_expenses.keys())

    amounts = [
        daily_expenses[date]
        for date in dates
    ]

    total_expenses = sum(amounts)

    # -----------------------------------------
    # CALCULATE A REALISTIC DAILY BASELINE
    # -----------------------------------------
    #
    # If transactions cover several dates,
    # calculate the average over the actual
    # calendar period.
    #
    # If all test transactions were entered
    # on one/few dates, don't treat the entire
    # amount as a daily recurring expense.
    #
    # Instead use a 30-day smoothing period.
    # -----------------------------------------

    if len(dates) >= 3:

        first_date = dates[0]
        last_date = dates[-1]

        calendar_days = (
            last_date - first_date
        ).days + 1

        calendar_days = max(
            calendar_days,
            1
        )

        average_daily_expense = (
            total_expenses / calendar_days
        )

    else:

        # Limited history.
        # Smooth expenses across 30 days.
        average_daily_expense = (
            total_expenses / 30
        )

    # -----------------------------------------
    # LINEAR REGRESSION
    # -----------------------------------------

    if len(dates) >= 3:

        X = np.arange(
            len(dates)
        ).reshape(-1, 1)

        y = np.array(amounts)

        model = LinearRegression()

        model.fit(X, y)

        future_indexes = np.arange(
            len(dates),
            len(dates) + days
        ).reshape(-1, 1)

        regression_predictions = (
            model.predict(future_indexes)
        )

        # Don't allow regression to produce
        # absurd values.
        historical_max = max(amounts)

        maximum_reasonable_daily_expense = (
            max(
                average_daily_expense * 2,
                historical_max
            )
        )

        predicted_values = [
            min(
                max(float(value), 0),
                maximum_reasonable_daily_expense
            )
            for value in regression_predictions
        ]

        model_used = "Linear Regression"

    else:

        # Not enough historical dates.
        predicted_values = [
            average_daily_expense
        ] * days

        model_used = (
            "30-Day Smoothed Average"
        )

    # -----------------------------------------
    # CREATE FORECAST
    # -----------------------------------------

    predictions = []

    today = datetime.now().date()

    for i in range(days):

        future_date = (
            today + timedelta(days=i + 1)
        )

        amount = max(
            0,
            float(predicted_values[i])
        )

        predictions.append({
            "date": future_date.isoformat(),
            "predicted_expense": round(
                amount,
                2
            )
        })

    predicted_total_expense = sum(
        item["predicted_expense"]
        for item in predictions
    )

    projected_balance = (
        current_balance -
        predicted_total_expense
    )

    return {
        "forecast_days": days,

        "average_daily_expense": round(
            average_daily_expense,
            2
        ),

        "predicted_total_expense": round(
            predicted_total_expense,
            2
        ),

        "current_balance": round(
            current_balance,
            2
        ),

        "projected_balance": round(
            projected_balance,
            2
        ),

        "model_used": model_used,

        "predictions": predictions
    }
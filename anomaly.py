import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

import models


def detect_anomalies(db: Session):

    # Only analyze EXPENSE transactions.
    # Income such as salary should not be treated
    # as suspicious simply because the amount is large.
    transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.transaction_type.ilike("expense")
        )
        .order_by(models.Transaction.date)
        .all()
    )

    # -----------------------------------------
    # NO EXPENSES
    # -----------------------------------------

    if not transactions:
        return {
            "total_transactions": 0,
            "anomalies_found": 0,
            "anomalies": [],
            "model_used": "Isolation Forest",
            "message": "No expense transactions available."
        }

    # -----------------------------------------
    # NOT ENOUGH DATA
    # -----------------------------------------

    if len(transactions) < 5:
        return {
            "total_transactions": len(transactions),
            "anomalies_found": 0,
            "anomalies": [],
            "model_used": "Isolation Forest",
            "message": "At least 5 expense transactions are recommended."
        }

    # -----------------------------------------
    # AMOUNT DATA
    # -----------------------------------------

    amounts = np.array([
        [float(transaction.amount)]
        for transaction in transactions
    ])

    # -----------------------------------------
    # ISOLATION FOREST
    # -----------------------------------------

    model = IsolationForest(
        n_estimators=200,
        contamination=0.15,
        random_state=42
    )

    predictions = model.fit_predict(amounts)

    scores = model.decision_function(amounts)

    anomalies = []

    # -----------------------------------------
    # FIND ANOMALIES
    # -----------------------------------------

    for transaction, prediction, score in zip(
        transactions,
        predictions,
        scores
    ):

        if prediction == -1:

            risk_score = (
                0.5 - float(score)
            ) * 100

            risk_score = max(
                0,
                min(
                    100,
                    risk_score
                )
            )

            anomalies.append({
                "id": transaction.id,
                "description": transaction.description,
                "amount": float(transaction.amount),
                "transaction_type": transaction.transaction_type,
                "category": transaction.category,
                "date": transaction.date.isoformat(),
                "risk_score": round(
                    risk_score,
                    2
                )
            })

    return {
        "total_transactions": len(transactions),
        "anomalies_found": len(anomalies),
        "anomalies": anomalies,
        "model_used": "Isolation Forest",
        "message": (
            "Only expense transactions are analyzed. "
            "Income transactions are excluded."
        )
    }
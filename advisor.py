from collections import defaultdict


def generate_financial_advice(
    transactions,
    forecast=None,
    anomalies=None
):
    """
    Generate personalized financial recommendations
    from transaction, forecast, and anomaly data.
    """

    # -----------------------------------------
    # CALCULATE INCOME AND EXPENSES
    # -----------------------------------------

    total_income = 0
    total_expenses = 0

    category_totals = defaultdict(float)

    for transaction in transactions:

        transaction_type = (
            transaction.transaction_type or ""
        ).lower()

        amount = float(
            transaction.amount or 0
        )

        if transaction_type == "income":

            total_income += amount

        elif transaction_type == "expense":

            total_expenses += amount

            category = (
                transaction.category
                or "Other"
            )

            category_totals[category] += amount

    # -----------------------------------------
    # BALANCE
    # -----------------------------------------

    balance = (
        total_income -
        total_expenses
    )

    # -----------------------------------------
    # SAVINGS RATE
    # -----------------------------------------

    if total_income > 0:

        savings_rate = (
            balance /
            total_income
        ) * 100

    else:

        savings_rate = 0

    # -----------------------------------------
    # TOP SPENDING CATEGORY
    # -----------------------------------------

    if category_totals:

        top_category = max(
            category_totals,
            key=category_totals.get
        )

        top_category_amount = (
            category_totals[
                top_category
            ]
        )

    else:

        top_category = None
        top_category_amount = 0

    # -----------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------

    recommendations = []

    # -----------------------------------------
    # INCOME CHECK
    # -----------------------------------------

    if total_income == 0:

        recommendations.append({
            "type": "warning",
            "title": "Add your income",
            "message": (
                "Record your income to get "
                "more accurate financial insights."
            )
        })

    # -----------------------------------------
    # EXPENSE VS INCOME
    # -----------------------------------------

    elif total_expenses > total_income:

        recommendations.append({
            "type": "danger",
            "title": "Expenses exceed income",
            "message": (
                "Your expenses are currently higher "
                "than your recorded income. Review "
                "your discretionary spending."
            )
        })

    else:

        expense_ratio = (
            total_expenses /
            total_income
        ) * 100

        if expense_ratio >= 80:

            recommendations.append({
                "type": "warning",
                "title": "High spending ratio",
                "message": (
                    f"Your expenses use approximately "
                    f"{expense_ratio:.1f}% of your income. "
                    "Consider reducing non-essential spending."
                )
            })

        elif expense_ratio >= 60:

            recommendations.append({
                "type": "info",
                "title": "Watch your spending",
                "message": (
                    f"About {expense_ratio:.1f}% of your income "
                    "is currently being spent. Keep your "
                    "discretionary expenses under control."
                )
            })

        else:

            recommendations.append({
                "type": "success",
                "title": "Healthy spending level",
                "message": (
                    f"Your expenses currently use about "
                    f"{expense_ratio:.1f}% of your income."
                )
            })

    # -----------------------------------------
    # SAVINGS ADVICE
    # -----------------------------------------

    if total_income > 0:

        if savings_rate >= 30:

            recommendations.append({
                "type": "success",
                "title": "Excellent savings potential",
                "message": (
                    f"Your current savings rate is "
                    f"{savings_rate:.1f}%. You have strong "
                    "potential to build your savings."
                )
            })

        elif savings_rate >= 20:

            recommendations.append({
                "type": "success",
                "title": "Good savings potential",
                "message": (
                    f"Your current savings rate is "
                    f"{savings_rate:.1f}%. Keep maintaining "
                    "your current spending discipline."
                )
            })

        elif savings_rate > 0:

            recommendations.append({
                "type": "info",
                "title": "Try to save more",
                "message": (
                    f"Your current savings rate is "
                    f"{savings_rate:.1f}%. Consider setting "
                    "a fixed monthly savings target."
                )
            })

        else:

            recommendations.append({
                "type": "danger",
                "title": "No current savings",
                "message": (
                    "Your recorded expenses are using "
                    "all of your available income. "
                    "Consider reducing unnecessary expenses."
                )
            })

    # -----------------------------------------
    # CATEGORY INSIGHT
    # -----------------------------------------

    if top_category:

        recommendations.append({
            "type": "category",
            "title": (
                f"Highest spending: {top_category}"
            ),
            "message": (
                f"You have spent ₹"
                f"{top_category_amount:,.0f} "
                f"on {top_category}. Review this category "
                "to identify possible savings."
            )
        })

    # -----------------------------------------
    # FORECAST INSIGHT
    # -----------------------------------------

    if forecast:

        predicted_expense = float(
            forecast.get(
                "predicted_total_expense",
                0
            )
        )

        projected_balance = float(
            forecast.get(
                "projected_balance",
                balance
            )
        )

        if projected_balance < 0:

            recommendations.append({
                "type": "danger",
                "title": "Negative projected balance",
                "message": (
                    "Your forecast indicates that your "
                    "balance could fall below zero. "
                    "Consider reducing upcoming expenses."
                )
            })

        elif predicted_expense > 0:

            recommendations.append({
                "type": "forecast",
                "title": "Upcoming expense forecast",
                "message": (
                    f"Your estimated expenses for the "
                    f"next 7 days are approximately ₹"
                    f"{predicted_expense:,.0f}."
                )
            })

    # -----------------------------------------
    # ANOMALY INSIGHT
    # -----------------------------------------

    if anomalies:

        anomaly_count = int(
            anomalies.get(
                "anomalies_found",
                0
            )
        )

        if anomaly_count > 0:

            recommendations.append({
                "type": "anomaly",
                "title": "Unusual spending detected",
                "message": (
                    f"The anomaly detection system found "
                    f"{anomaly_count} unusual expense"
                    f"{'s' if anomaly_count != 1 else ''}. "
                    "Review these transactions."
                )
            })

        else:

            recommendations.append({
                "type": "success",
                "title": "Spending looks consistent",
                "message": (
                    "No significant unusual expense "
                    "patterns were detected."
                )
            })

    # -----------------------------------------
    # EMERGENCY FUND
    # -----------------------------------------

    if balance > 0:

        recommendations.append({
            "type": "general",
            "title": "Build an emergency reserve",
            "message": (
                "Consider keeping part of your available "
                "balance as an emergency fund."
            )
        })

    # -----------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------

    return {
        "status": "success",

        "summary": {
            "income": round(
                total_income,
                2
            ),

            "expenses": round(
                total_expenses,
                2
            ),

            "balance": round(
                balance,
                2
            ),

            "savings_rate": round(
                savings_rate,
                2
            ),

            "top_category": top_category,

            "top_category_amount": round(
                top_category_amount,
                2
            )
        },

        "recommendations": recommendations,

        "model_used": "AI Financial Advisor"
    }
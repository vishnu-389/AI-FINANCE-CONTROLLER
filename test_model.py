import joblib

model = joblib.load("expense_category_model.pkl")

test_transactions = [
    "Pizza from restaurant",
    "Uber to college",
    "Electricity payment",
    "Amazon order",
    "Monthly house rent",
    "Netflix subscription",
    "Petrol for bike",
    "Doctor consultation",
    "Flight booking",
]

print("\nAI EXPENSE CATEGORIZATION\n")

for transaction in test_transactions:

    prediction = model.predict([transaction])[0]

    print(
        f"{transaction:<30} -> {prediction}"
    )
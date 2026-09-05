import joblib
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "expense_category_model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_category(description: str):
    prediction = model.predict([description])[0]

    probabilities = model.predict_proba([description])[0]

    confidence = max(probabilities)

    return {
        "category": prediction,
        "confidence": round(float(confidence) * 100, 2)
    }
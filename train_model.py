import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

data = pd.read_csv("training_data.csv")

X = data["description"]
y = data["category"]

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000
        )
    )
])

model.fit(X, y)

joblib.dump(model, "expense_category_model.pkl")

print("AI expense categorization model trained successfully!")
print("Categories:", sorted(y.unique()))
print("Model saved as expense_category_model.pkl")
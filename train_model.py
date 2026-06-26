import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import joblib

# Dummy dataset

data = {
    'income': [30000, 50000, 100000, 25000, 70000],
    'credit_score': [600, 750, 800, 500, 720],
    'loan_amount': [200000, 500000, 800000, 150000, 300000],
    'approved': [0, 1, 1, 0, 1]
}


df = pd.DataFrame(data)

X = df[['income', 'credit_score', 'loan_amount']]
y = df['approved']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = XGBClassifier()
model.fit(X_train, y_train)

joblib.dump(model, 'credit_model.pkl')

print("Model trained successfully")

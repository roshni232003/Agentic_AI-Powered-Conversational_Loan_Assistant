import joblib
import numpy as np

model = joblib.load('ml/credit_model.pkl')


def check_credit_risk(income, credit_score, loan_amount):
    data = np.array([[income, credit_score, loan_amount]])

    prediction = model.predict(data)[0]

    return "APPROVED" if prediction == 1 else "REJECTED"

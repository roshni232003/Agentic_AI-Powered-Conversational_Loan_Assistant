from fastapi import FastAPI, UploadFile, File
from agents.master_agent import MasterAgent
import shutil
import os

app = FastAPI()

master = MasterAgent()


@app.get("/")
def home():
    return {"message": "AI Loan Assistant Running"}


@app.post("/apply-loan")
async def apply_loan(
    name: str,
    phone: str,
    income: float,
    credit_score: int,
    loan_amount: float,
    document: UploadFile = File(...)
):

    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{document.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(document.file, buffer)

    customer_data = {
        "name": name,
        "phone": phone,
        "income": income,
        "credit_score": credit_score,
        "loan_amount": loan_amount
    }

    result = master.process_loan(customer_data, file_path)

    return result

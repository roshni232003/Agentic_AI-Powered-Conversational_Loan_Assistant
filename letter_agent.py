from fpdf import FPDF
import os


def generate_sanction_letter(name, amount, tenure):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="Loan Sanction Letter", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Dear {name},", ln=True)
    pdf.cell(200, 10, txt=f"Your loan of INR {amount} has been approved.", ln=True)
    pdf.cell(200, 10, txt=f"Loan tenure: {tenure} months", ln=True)

    os.makedirs("generated_letters", exist_ok=True)

    path = f"generated_letters/{name}_loan_letter.pdf"

    pdf.output(path)

    return path

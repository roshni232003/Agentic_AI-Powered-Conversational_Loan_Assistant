from agents.sales_agent import explain_loan_options
from agents.worker_agent import collect_customer_data
from agents.verification_agent import verify_document
from agents.credit_agent import check_credit_risk
from agents.approval_agent import final_decision
from agents.letter_agent import generate_sanction_letter


class MasterAgent:

    def process_loan(self, customer_data, document_path):

        sales_response = explain_loan_options(
            "Explain available personal loan options"
        )

        db_response = collect_customer_data(customer_data)

        verification = verify_document(document_path)

        credit = check_credit_risk(
            customer_data['income'],
            customer_data['credit_score'],
            customer_data['loan_amount']
        )

        decision = final_decision(
            verification['verified'],
            credit
        )

        pdf_path = None

        if decision == "LOAN APPROVED":
            pdf_path = generate_sanction_letter(
                customer_data['name'],
                customer_data['loan_amount'],
                24
            )

        return {
            "sales_response": sales_response,
            "database_status": db_response,
            "verification": verification,
            "credit_result": credit,
            "decision": decision,
            "pdf": pdf_path
        }

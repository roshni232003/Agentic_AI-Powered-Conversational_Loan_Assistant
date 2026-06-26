def final_decision(verification_status, credit_result):

    if not verification_status:
        return "REJECTED - DOCUMENT FAILED"

    if credit_result == "APPROVED":
        return "LOAN APPROVED"

    return "LOAN REJECTED"

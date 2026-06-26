from database.db import cursor, conn


def collect_customer_data(data):
    query = """
    INSERT INTO customers
    (name, phone, income, credit_score, loan_amount, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        data['name'],
        data['phone'],
        data['income'],
        data['credit_score'],
        data['loan_amount'],
        'PENDING'
    )

    cursor.execute(query, values)
    conn.commit()

    return "Customer data stored successfully"

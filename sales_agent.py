from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.5)


def explain_loan_options(user_query):
    prompt = f"""
    You are a friendly loan sales assistant.
    Explain loan offers simply.

    Customer Query:
    {user_query}
    """

    response = llm.invoke(prompt)
    return response.content

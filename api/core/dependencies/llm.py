import os
from dotenv import load_dotenv
from openai import OpenAI
from api.core.config import settings

load_dotenv()

#client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
client = OpenAI(api_key=settings.openai_api_key)


def analyze_emails(emails, question):

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "system",
                "content": "You are my assistant, your job is to read all the email information i provide and use the information inthere to answer my questions. You respond with text and reference to which of the emails I provided that informed that response. If the response is not avaialble in the data let me know",
            },
            {
                "role": "user",
                "content": f"Here are the emails:\n{emails}\n\nMy question is: {question}",
            },
        ],
    )
    return response.output_text


emails_data = "Email 1: Subject: ... Body: ...\nEmail 2: Subject: ... Body: ..."
question = "What was discussed about the new pricing strategy?"

answer = analyze_emails(emails_data, question)
print(answer)
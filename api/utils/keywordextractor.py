from gradio_client import Client
import re

client = Client("jsperez/transformer3-H2-keywordextractor")


def extract_keywords(text):

    result = client.predict(param_0=text, api_name="/predict")
    match = re.search(r"summary_text='(.*?)'", result)
    if match:
        extracted_text = match.group(1)
        keywords_list = [keyword.strip() for keyword in extracted_text.split(",")]
        return keywords_list
    else:
        return [text]
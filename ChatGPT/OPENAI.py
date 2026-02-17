from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

def main():
    messages = build_message()
    response = get_response(messages)

    print(response)

def build_message():
    question = input("What do you want to ask ChatGPT? ")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question}
    ]

    return messages

def get_response(prompt, temperature=0, max_tokens=100):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature = temperature,
        max_tokens = max_tokens
    )
    return response.choices[0].message.content

main()

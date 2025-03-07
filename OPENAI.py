from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def main():
    messages = build_message()
    response = get_response(messages)

    print("\nChatGPT:", response)

def build_message():
    question = input("What do you want to ask ChatGPT? ")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question}
    ]
    return messages

def get_response(prompt, temperature=0, max_tokens=100):
    client = OpenAI()  # No need to pass API key manually
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    main()

import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model="open-mistral-nemo", 
    messages=[
        {"role": "user", "content": "What is the best French cheese?"},
    ],
)

print(chat_response.choices[0].message.content)

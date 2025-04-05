import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

chat_response = client.agents.complete(
    agent_id="ag:b01ddf1b:20250405:untitled-agent:fee26ae0",
    messages=[
        {
            "role": "user",
            "content": "What is the best French cheese?",
        },
    ],
)
print(chat_response.choices[0].message.content)
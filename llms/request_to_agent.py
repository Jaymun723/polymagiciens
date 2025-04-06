import os
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

def request_to_agent(query, agent):
    chat_history = [
        SystemMessage(content=agent.systematic_prompt),
        UserMessage(content=query),
    ]

    chat_response = client.chat.complete(
        model=agent.model_name,
        messages=chat_history,
        temperature=agent.temperature
    )

    return chat_response.choices[0].message.content
"""
First hand try
"""

import logging
import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_ID = "anthropic.claude-3-7-sonnet-20250219-v1:0"

conversation = []


def talk_to_client(client):
    user_input = input()
    while not user_input == "stop":
        conversation.append({"role": "user", "content": [{"text": user_input}]})

        response = client.converse(
            modelId=MODEL_ID,
            messages=conversation,
        )

        print(response["output"]["message"]["content"][0]["text"])

        conversation.append(response["output"]["message"])

        user_input = input()


def main():
    bedrock_client = boto3.client("bedrock-runtime")

    print(boto3.client("bedrock").list_foundation_models())

    talk_to_client(bedrock_client)

    logger.info("Done.")


if __name__ == "__main__":
    main()

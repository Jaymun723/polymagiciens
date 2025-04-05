"""
Lists the available Amazon Bedrock models.
"""

import logging
import json
import boto3


from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_ID = "mistral.mistral-large-2407-v1:0"

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

    talk_to_client(bedrock_client)

    logger.info("Done.")


if __name__ == "__main__":
    main()

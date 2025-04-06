from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch


# Load model and tokenizer
model_name = "roberta-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


def comment_score(post: str, comment: str):
    # Tokenize inputs
    inputs = tokenizer(
        post, comment, return_tensors="pt", truncation=True, max_length=512
    )

    # Get model predictions
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert logits to probabilities
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    index = torch.argmax(probabilities).item()

    if index == 0:
        return -1
    elif index == 1:
        return 0
    else:
        return 1

    # Probabilities for contradiction, neutral, entailment


#     entailment_prob = probabilities[0][2].item()  # Index 2 for entailment

#     return entailment_prob


# def calculate_score(label, score):
#     if score > 0.7:
#         if label == "CONTRADICTION":
#             return -1
#         elif label == "ENTAILMENT":
#             return 1
#     else:
#         return 0


# def comment_score(post: str, comment: str) -> float:
#     predictor = Predictor(
#         endpoint_name="huggingface-pytorch-inference-2025-04-05-23-31-42-092"
#     )
#     predictor.serializer = JSONSerializer()

#     payload = {"inputs": f"{post} </s> {comment}"}

#     response = predictor.predict(payload)
#     result = json.loads(response.decode("utf-8"))

#     for item in result:
#         label = item["label"]
#         score = item["score"]

#     return calculate_score(label, score)

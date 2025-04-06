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

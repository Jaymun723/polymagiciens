from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Load model and tokenizer
model_name = "roberta-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


def calculate_match_score(post, comment):
    # Tokenize inputs
    inputs = tokenizer(
        post, comment, return_tensors="pt", truncation=True, max_length=512
    )

    # Get model predictions
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert logits to probabilities
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # Probabilities for contradiction, neutral, entailment
    entailment_prob = probabilities[0][2].item()  # Index 2 for entailment

    return entailment_prob


# Example usage
post = "The new policy is beneficial for everyone."
comments = [
    "I completely agree, this policy helps a lot.",
    "This is the worst decision they've made.",
    "The policy was introduced last week.",
]

for comment in comments:
    score = calculate_match_score(post, comment)
    print(f"Comment: {comment}\nScore: {score:.2f}\n")

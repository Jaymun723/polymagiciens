# deploy_nli_sagemaker.py

from sagemaker.huggingface import HuggingFaceModel
from sagemaker.predictor import Predictor
import sagemaker
import boto3
import json
import time

# -------------------------
# Configuration AWS/SageMaker
# -------------------------
sess = sagemaker.Session()
role = "arn:aws:iam::<your-account-id>:role/service-role/AmazonSageMaker-ExecutionRole-XXXX"  # TODO: Remplacer par votre ARN IAM

# -------------------------
# Étape 1 : Déployer le modèle RoBERTa-MNLI
# -------------------------
hub = {
    'HF_MODEL_ID': 'roberta-large-mnli',
    'HF_TASK': 'text-classification'
}

huggingface_model = HuggingFaceModel(
    transformers_version='4.26',
    pytorch_version='1.13',
    py_version='py39',
    env=hub,
    role=role
)

print("\nDeploying model... (this may take a few minutes)")
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',  # ou ml.g4dn.xlarge pour GPU
)

print("\nModel deployed!")

# -------------------------
# Étape 2 : Fonction d'appel au modèle
# -------------------------
def calculate_match_score(predictor: Predictor, post: str, comment: str) -> float:
    payload = {
        "inputs": f"{post} </s> {comment}"
    }
    response = predictor.predict(json.dumps(payload).encode("utf-8"))
    result = json.loads(response.decode("utf-8"))

    scores = {item['label']: item['score'] for item in result[0]}
    return scores.get("ENTAILMENT", 0.0)

# -------------------------
# Étape 3 : Tester avec des exemples
# -------------------------
post = "The new policy is beneficial for everyone."
comments = [
    "I completely agree, this policy helps a lot.",
    "This is the worst decision they've made.",
    "The policy was introduced last week."
]

print("\nScoring example comments:")
for comment in comments:
    score = calculate_match_score(predictor, post, comment)
    print(f"Comment: {comment}\nScore: {score:.2f}\n")

# -------------------------
# Étape 4 : Nettoyage (optionnel)
# -------------------------
# predictor.delete_endpoint()  # À décommenter pour supprimer l'endpoint si plus utilisé

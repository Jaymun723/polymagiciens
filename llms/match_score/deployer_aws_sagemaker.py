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
role = "arn:aws:iam::290971503872:role/MySageMakerExecutionRole" 

# # -------------------------
# # Étape 1 : Déployer le modèle RoBERTa-MNLI
# # -------------------------
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
# Étape 4 : Nettoyage (optionnel)
# -------------------------
# predictor.delete_endpoint()  # À décommenter pour supprimer l'endpoint si plus utilisé

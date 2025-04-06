from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
import json


def calculate_score(label,score):
    if score>0.7:
        if label=='CONTRADICTION':
            return -1
        elif label=='ENTAILMENT':
            return 1 
    else :
        return 0

def comment_score(post: str, comment: str) -> float:
    predictor = Predictor(endpoint_name="huggingface-pytorch-inference-2025-04-05-23-31-42-092")
    predictor.serializer = JSONSerializer()  

    payload = {
        "inputs": f"{post} </s> {comment}"
    }

    response = predictor.predict(payload)
    result = json.loads(response.decode("utf-8"))

    for item in result : 
        label = item['label']
        score = item['score']

    return calculate_score(label,score)

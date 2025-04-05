import pandas as pd
from Fact_check_v2 import post_to_grade

import pandas as pd

df = pd.read_csv("combined_dataset.csv")

bon = 0
total = 0
for idx, row in df.iterrows():
    evaluation = 1 if ((1 - post_to_grade(row["title"] , row["text"], row["date"]) / 100)>0.2) else 0
    result = row["misinformation"]
    total += 1
    bon += (evaluation == result)
    print(f"Evaluation: {evaluation}, Result: {result}, Score: {bon/total}")

df["score"] = df.apply(
    lambda row: abs(
        post_to_grade(row["text"], "05/04/2025") / 100 - row["misinformation"]
    ),
    axis=1,
)

print(df[["text", "misinformation", "score"]].head())

average_score = df["score"].mean()
print(f"Score moyen du modèle : {average_score}")

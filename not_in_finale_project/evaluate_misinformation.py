import pandas as pd
from llms.request_factcheck import post_to_grade

df = pd.read_csv("not_in_finale_project/combined_dataset.csv")

bon = 0
total = 0
for idx, row in df.iterrows():
    n = post_to_grade(row["title"] , row["text"], row["date"])
    evaluation = 1 if ((1 - n / 100)>0.2) else 0
    result = row["misinformation"]
    total += 1
    bon += (evaluation == result)
    print(f"Evaluation: {evaluation}, Result: {result}, Real result: {1-n/100}, Score: {bon/total}")

df["score"] = df.apply(
    lambda row: abs(
        post_to_grade(row["text"], "05/04/2025") / 100 - row["misinformation"]
    ),
    axis=1,
)

print(df[["text", "misinformation", "score"]].head())

average_score = df["score"].mean()
print(f"Score moyen du modèle : {average_score}")

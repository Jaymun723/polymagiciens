import pandas as pd
from Fact_chek_v1 import post_to_grade

df = pd.read_csv("combined_dataset.csv")

for idx, row in df.iterrows():
    evalation = 1 - post_to_grade(row["title"] + row["text"], row["date"]) / 100
    result = row["misinformation"]
    print(f"Evaluation: {evalation}, Result: {result}")

df["score"] = df.apply(
    lambda row: abs(
        post_to_grade(row["text"], "05/04/2025") / 100 - row["misinformation"]
    ),
    axis=1,
)

print(df[["text", "misinformation", "score"]].head())

average_score = df["score"].mean()
print(f"Score moyen du modèle : {average_score}")

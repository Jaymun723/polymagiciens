
from pg_reddit_driver import RedditDB
import pandas as pd

db = RedditDB()

# --- 1. Users ---
users = db.get_users()
user_nodes = pd.DataFrame({
    "id": [f"user_{u[0]}" for u in users],
    "label": ["User"] * len(users),
    "type": ["user"] * len(users),
    "text_or_title": [u[1] for u in users]
})

# --- 2. Posts ---
posts = db.get_posts()
post_nodes = pd.DataFrame({
    "id": [f"post_{p[0]}" for p in posts],
    "label": ["Post"] * len(posts),
    "type": ["post"] * len(posts),
    "text_or_title": [p[2] for p in posts]  # p[2] = title
})

# --- 3. Comments ---
comments = db.get_comments()
comment_nodes = pd.DataFrame({
    "id": [f"comment_{c[0]}" for c in comments],
    "label": ["Comment"] * len(comments),
    "type": ["comment"] * len(comments),
    "text_or_title": [c[3] for c in comments]  # c[3] = content
})

# --- Fusionner tous les nœuds ---
nodes = pd.concat([user_nodes, post_nodes, comment_nodes], ignore_index=True)

# --- 4. Edges : AUTHORED by User ---
user_post_edges = pd.DataFrame({
    "from": [f"user_{p[1]}" for p in posts],
    "to": [f"post_{p[0]}" for p in posts],
    "label": ["AUTHORED"] * len(posts)
})

user_comment_edges = pd.DataFrame({
    "from": [f"user_{c[1]}" for c in comments],
    "to": [f"comment_{c[0]}" for c in comments],
    "label": ["AUTHORED"] * len(comments)
})

# --- 5. Edges : REPLIED_TO (comment -> post or comment) ---
comment_edges = []
for c in comments:
    parent_id = c[2]  # c[2] = post_id
    # naïvement lier au post, pas aux commentaires imbriqués (on peut améliorer)
    comment_edges.append({
        "from": f"comment_{c[0]}",
        "to": f"post_{parent_id}",
        "label": "REPLIED_TO"
    })

replied_to_edges = pd.DataFrame(comment_edges)

# --- Fusionner tous les liens ---
edges = pd.concat([user_post_edges, user_comment_edges, replied_to_edges], ignore_index=True)

# --- Sauvegarde ---
nodes.to_csv("nodes.csv", index=False)
edges.to_csv("edges.csv", index=False)

print("✅ Export terminé : nodes.csv et edges.csv générés.")

import networkx as nx
from graph.pg_reddit_driver import (
    RedditDB,
)  # assuming your class is saved in reddit_db.py
import pandas as pd


def build_graph_from_db(db: RedditDB) -> nx.DiGraph:
    G = nx.DiGraph()

    # --- Add Users ---
    for user_id, user_name, score in db.get_users():
        G.add_node(user_id, label="User", name=user_name, weight=score)

    # --- Add Posts ---
    for (
        post_id,
        author_id,
        title,
        content,
        subreddit,
        upvotes,
        score,
        treated,
        date,
    ) in db.get_posts():
        G.add_node(post_id, label="Post", title=title, weight=score)
        if author_id:
            G.add_edge(author_id, post_id, label="posted", weight=1.0)

    # --- Add Comment relations as edges ---
    for (
        comment_id,
        author_id,
        post_id,
        content,
        upvotes,
        score,
        treated,
        date,
    ) in db.get_comments():
        if author_id and post_id:
            G.add_edge(author_id, post_id, label="commented_on", weight=score / 100.0)

    return G


def save_graph_to_csv(G: nx.DiGraph, nodes_csv: str, edges_csv: str):
    nodes_data = [
        {
            "id": n,
            "label": d["label"],
            "text_or_title": d.get("title", d.get("name", "")),
            "weight": d["weight"],
        }
        for n, d in G.nodes(data=True)
    ]
    pd.DataFrame(nodes_data).to_csv(nodes_csv, index=False)

    edges_data = [
        {"from": u, "to": v, "label": d["label"], "weight": d["weight"]}
        for u, v, d in G.edges(data=True)
    ]
    pd.DataFrame(edges_data).to_csv(edges_csv, index=False)

    print(f"Graph saved to:\n - {nodes_csv}\n - {edges_csv}")


# if __name__ == "__main__":
#     db = RedditDB()
#     G = build_graph_from_db(db)
#     save_graph_to_csv(G, "../graph_output/nodes.csv", "graph_info/edges.csv")

#     print("Graph built!")
#     print("Nodes:", G.number_of_nodes())
#     print("Edges:", G.number_of_edges())

from graph.build_graph import build_graph_from_db, save_graph_to_csv
from graph.pg_reddit_driver import RedditDB
import os


def build_graph():
    db = RedditDB()
    G = build_graph_from_db(db)

    base_path = os.path.join(os.getcwd(), "output")

    save_graph_to_csv(
        G, os.path.join(base_path, "nodes.csv"), os.path.join(base_path, "edges.csv")
    )

    print("Graph built!")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

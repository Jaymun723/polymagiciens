from graph.build_graph import build_graph_from_db, save_graph_to_csv
from graph.pg_reddit_driver import RedditDB
from graph.lissage import load_graph_from_csv, smooth_node_weights
import os


def build_graph():
    db = RedditDB()
    G_raw = build_graph_from_db(db)

    base_path = os.path.join(os.getcwd(), "output")
    nodes_raw_path = os.path.join(base_path, "nodes_raw.csv")
    nodes_path = os.path.join(base_path, "nodes.csv")
    edges_raw_path = os.path.join(base_path, "edges_raw.csv")
    edges_path = os.path.join(base_path, "edges.csv")

    save_graph_to_csv(G_raw, nodes_raw_path, edges_raw_path)

    print("Raw graph built!")
    print("Nodes:", G_raw.number_of_nodes())
    print("Edges:", G_raw.number_of_edges())

    G = smooth_node_weights(G_raw, alpha=0.5)
    print("Final graph build")
    save_graph_to_csv(G, nodes_path, edges_path)

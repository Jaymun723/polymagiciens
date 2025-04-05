import pandas as pd
import networkx as nx
from pyvis.network import Network

def build_and_visualize_graph(nodes_csv="nodes.csv", edges_csv="edges.csv", output_html="reddit_graph.html"):
    # Lire les CSV
    nodes_df = pd.read_csv(nodes_csv)
    edges_df = pd.read_csv(edges_csv)

    # Créer le graphe dirigé
    G = nx.DiGraph()

    # Ajouter les sommets
    for _, row in nodes_df.iterrows():
        G.add_node(
            row["id"],
            label=row["id"],
            title=row.get("text_or_title", ""),
            type=row["label"],
            color=(
                "#f94144" if row["label"] == "User" else
                "#f3722c" if row["label"] == "Post" else
                "#577590"
            )
        )

    # Ajouter les arêtes
    for _, row in edges_df.iterrows():
        G.add_edge(
            row["from"],
            row["to"],
            label=row["label"]
        )

    # Pyvis pour visualisation
    net = Network(height="750px", width="100%", directed=True)
    net.from_nx(G)
    net.show_buttons(filter_=['physics'])
    net.show(output_html)
    print(f"✅ Graphe exporté dans {output_html}")


build_and_visualize_graph("/home/ines_bichon/projets-vscode/hackathon-essec/polymagiciens/graph/nodes.csv","/home/ines_bichon/projets-vscode/hackathon-essec/polymagiciens/graph/edges.csv")
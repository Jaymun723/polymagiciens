import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def plot_graph_matplotlib(nodes_csv, edges_csv, output_file="graph.png"):
    # Lire les CSV
    nodes_df = pd.read_csv(nodes_csv)
    edges_df = pd.read_csv(edges_csv)

    # Créer le graphe
    G = nx.DiGraph()

    # Ajouter les nœuds avec types
    for _, row in nodes_df.iterrows():
        G.add_node(row['id'], label=row['label'], text=row.get('text_or_title', ''))

    # Ajouter les arêtes avec poids
    for _, row in edges_df.iterrows():
        G.add_edge(row['from'], row['to'],
                   label=row.get('label', ''),
                   weight=row.get('weight', 1.0))

    # Layout automatique (spring)
    pos = nx.spring_layout(G, seed=42)

    # Obtenir les poids des arêtes pour les largeurs
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    widths = [1 + 2 * w for w in weights]  # adapter les facteurs selon le rendu

    # Couleurs des nœuds selon le type
    node_colors = []
    for node in G.nodes(data=True):
        node_type = node[1]['label']
        color = "#f94144" if node_type == "User" else "#f3722c" if node_type == "Post" else "#577590"
        node_colors.append(color)

    # Dessiner les éléments
    plt.figure(figsize=(10, 7))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700)
    nx.draw_networkx_edges(G, pos, width=widths, arrows=True, alpha=0.6)
    nx.draw_networkx_labels(G, pos, font_size=10, font_color="white")

    # Ajouter les labels des arêtes (optionnel)
    edge_labels = {(u, v): G[u][v]['label'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='gray')

    plt.title("Graph Visualization with Matplotlib")
    plt.axis("off")
    plt.tight_layout()

    # Enregistrer le graphe dans un fichier
    plt.savefig(output_file, format="png", dpi=300)  # Format et résolution ajustables
    print(f"Graphe enregistré dans : {output_file}")

    # Afficher le graphe
    plt.show()

# Exemple d'utilisation
plot_graph_matplotlib("nodes.csv", "edges.csv", output_file="graph_output.png")


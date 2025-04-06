import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.cm as cm
import matplotlib.colors as mcolors


def plot_graph_custom(nodes_csv, edges_csv, output_path):
    # Charger les fichiers
    nodes_df = pd.read_csv(nodes_csv)
    edges_df = pd.read_csv(edges_csv)

    # Nettoyer les labels
    nodes_df["label"] = nodes_df["label"].str.capitalize()

    # Créer le graphe
    G = nx.DiGraph()

    for _, row in nodes_df.iterrows():
        G.add_node(row["id"], type=row["label"], weight=row["weight"])

    for _, row in edges_df.iterrows():
        if row["from"] in G and row["to"] in G:
            G.add_edge(row["from"], row["to"], label=row["label"], weight=row["weight"])
        else:
            print(f"⚠️ Arête ignorée (noeud manquant) : {row['from']} -> {row['to']}")

    pos = nx.spring_layout(G, seed=50)

    ### --- Couleurs des nœuds ---
    node_weights = [G.nodes[n]["weight"] for n in G.nodes()]
    node_min, node_max = min(node_weights), max(node_weights)

    node_cmap = cm.get_cmap("bwr")
    if node_min < 0 and node_max > 0:
        node_norm = mcolors.TwoSlopeNorm(vmin=node_min, vcenter=0, vmax=node_max)
    else:
        node_norm = mcolors.Normalize(vmin=node_min, vmax=node_max)

    node_colors = []
    for w in node_weights:
        if w == 0:
            node_colors.append("lightgray")
        else:
            node_colors.append(node_cmap(node_norm(w)))

    ### --- Arêtes ---
    edge_styles = []
    edge_widths = []
    for u, v in G.edges():
        w = G[u][v]["weight"]
        edge_styles.append("dashed" if w < 0 else "solid")
        edge_widths.append(1 + abs(w) * 4)  # Adapter le facteur selon rendu

    edge_colors = ["gray" for _ in G.edges()]  # Toutes grises

    ### --- Dessin ---
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800)
    nx.draw_networkx_labels(G, pos, font_size=10, font_color="black")

    # Tracer arêtes individuellement pour pouvoir styliser
    for (u, v), color, width, style in zip(
        G.edges(), edge_colors, edge_widths, edge_styles
    ):
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(u, v)],
            edge_color=color,
            width=width,
            style=style,
            alpha=0.8,
            arrows=True,
        )

    # Labels des arêtes
    edge_labels = {(u, v): G[u][v]["label"] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.title("Graphe avec arêtes grises, styles selon signe, largeur selon intensité")
    plt.axis("off")
    plt.savefig(output_path)
    plt.tight_layout()
    plt.show()


# Exemple d'utilisation
plot_graph_custom("nodes.csv", "edges.csv", "image_graphe.png")

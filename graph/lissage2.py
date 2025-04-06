import pandas as pd
import os
import networkx as nx

INPUT_DIR = "graph_info"
OUTPUT_DIR = "graph_lissage_info"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_graph_from_csv(nodes_path, edges_path):
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    G = nx.DiGraph()

    for _, row in nodes_df.iterrows():
        G.add_node(row["id"], label=row["label"], text=row.get("text_or_title", ""), weight=row.get("weight", 0))

    for _, row in edges_df.iterrows():
        if row["from"] in G and row["to"] in G:
            G.add_edge(row["from"], row["to"], label=row["label"], weight=row["weight"])
    return G, nodes_df, edges_df

def save_graph_to_csv(G, nodes_out, edges_out):
    nodes_data = []
    for n, data in G.nodes(data=True):
        nodes_data.append({
            "id": n,
            "label": data.get("label", ""),
            "text_or_title": data.get("text", ""),
            "weight": data.get("weight", 0)
        })
    nodes_df = pd.DataFrame(nodes_data)
    nodes_df.to_csv(nodes_out, index=False)

    edges_data = []
    for u, v, data in G.edges(data=True):
        edges_data.append({
            "from": u,
            "to": v,
            "label": data.get("label", ""),
            "weight": data.get("weight", 1.0)
        })
    edges_df = pd.DataFrame(edges_data)
    edges_df.to_csv(edges_out, index=False)

def smooth_node_weights(G, alpha=0.5):
    new_weights = {}
    for node in G.nodes:
        neighbor_weights = []
        for neighbor in G.predecessors(node):
            w = G[neighbor][node]["weight"]
            neighbor_weights.append(G.nodes[neighbor].get("weight", 0) * w)
        for neighbor in G.successors(node):
            w = G[node][neighbor]["weight"]
            neighbor_weights.append(G.nodes[neighbor].get("weight", 0) * w)

        if neighbor_weights:
            smooth_val = alpha * G.nodes[node].get("weight", 0) + (1 - alpha) * (sum(neighbor_weights) / len(neighbor_weights))
        else:
            smooth_val = G.nodes[node].get("weight", 0)
        new_weights[node] = smooth_val

    nx.set_node_attributes(G, new_weights, "weight")
    return G

# === Pipeline ===
G, _, _ = load_graph_from_csv(f"{INPUT_DIR}/nodes.csv", f"{INPUT_DIR}/edges.csv")
G = smooth_node_weights(G, alpha=0.5)
save_graph_to_csv(G, f"{OUTPUT_DIR}/nodes.csv", f"{OUTPUT_DIR}/edges.csv")
print("✅ Graphe lissé exporté dans graph_lissage_info/")

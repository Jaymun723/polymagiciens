import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as splinalg

def smooth_node_weights(n_nodes, edges, proximities, initial_weights, lam=1.0):
    """
    - n_nodes: nombre total de noeuds
    - edges: liste de tuples (i, j) pour les arêtes
    - proximities: liste des poids P_ij (même ordre que edges)
    - initial_weights: np.array de taille (n_nodes,)
    - lam: facteur de régularisation (lambda)
    """

    # Construction du Laplacien pondéré L
    row, col, data = [], [], []

    for (i, j), p in zip(edges, proximities):
        # termes diagonaux
        row.extend([i, j])
        col.extend([i, j])
        data.extend([p, p])

        # termes hors diagonale
        row.extend([i, j])
        col.extend([j, i])
        data.extend([-p, -p])

    L = sp.coo_matrix((data, (row, col)), shape=(n_nodes, n_nodes)).tocsc()

    # (L + lambda * I)
    I = sp.eye(n_nodes)
    A = L + lam * I

    # côté droit : lambda * w0
    b = lam * initial_weights

    # résolution du système linéaire
    w_smoothed = splinalg.spsolve(A, b)

    return w_smoothed
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import reverse_cuthill_mckee

from scipy.cluster import hierarchy


def _preprocess(adj_mat):
    assert adj_mat.shape[0] == adj_mat.shape[1]
    if isinstance(adj_mat, pd.DataFrame):
        adj_mat = adj_mat.values
    return adj_mat


def reorder(adj_mat, idx):
    """Reorder rows and columns of a square matrix based on given indices."""
    adj_mat = adj_mat.copy()
    if isinstance(adj_mat, pd.DataFrame):
        adj_mat = adj_mat.iloc[idx, :]
        adj_mat = adj_mat.iloc[:, idx]
    else:
        adj_mat = adj_mat[idx, :]
        adj_mat = adj_mat[:, idx]
    return adj_mat


def count_perm(adj_mat):
    """Column permutation based on nonzero count."""
    _adj_mat = _preprocess(adj_mat)
    idx = np.argsort(np.sum(_adj_mat != 0, axis=1), kind='stable')  # kind=stable is important
    return reorder(adj_mat, idx)


def pairwise_cosine(mat):
    """Computes Cosine Similarity for each pair of rows in the given matrix."""
    def cosine_similarity(a, b):
        return (a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b))

    n = len(mat)
    dist_mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = cosine_similarity(mat[i], mat[j])
            dist_mat[i, j] = dist
            dist_mat[j, i] = dist

    dist_mat[np.isnan(dist_mat)] = 0

    return dist_mat


def nearest_neigbor_perm(adj_mat):
    """Column permutation based on Nearest Neighbor heuristic that uses Cosine Similarity."""
    # compute distance matrix
    dist_mat = pairwise_cosine(adj_mat.values)
    n = len(dist_mat)

    # find first strongest connection
    idx = dist_mat.argmax(1)
    dists = dist_mat[np.arange(n), idx]
    start_id = dists.argmax()

    # apply nearest neighbor search
    path = [start_id]
    to_visit_mask = np.ones(n, dtype=bool)
    to_visit_mask[start_id] = False
    while np.any(to_visit_mask):
        curr_id = path[-1]
        dist = dist_mat[curr_id]
        dist[~to_visit_mask] = -1
        next_id = dist.argmax()
        to_visit_mask[next_id] = False
        path.append(next_id)

    idx = np.array(path)
    return reorder(adj_mat, idx)


def rcm_perm(adj_mat):
    """Column permutation based on Reverse Cuthill-McKee algorithm."""
    _adj_mat = _preprocess(adj_mat)
    graph = csr_matrix(_adj_mat)
    idx = reverse_cuthill_mckee(graph, symmetric_mode=True)
    return reorder(adj_mat, idx)


def hierarchical_clustering_perm(adj_mat, linkage='complete'):
    """Column permutation based on hierarchical clustering algorithm."""
    _adj_mat = _preprocess(adj_mat)

    # ['single', 'complete', 'average', 'weighted', 'centroid', 'median', 'ward']
    Y = hierarchy.linkage(_adj_mat, method=linkage, metric='euclidean', optimal_ordering=True)
    Z = hierarchy.dendrogram(Y, orientation='right', no_plot=True)
    idx = Z['leaves']
    return reorder(adj_mat, idx)

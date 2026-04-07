import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_connectivity_similarity(mat):
    """Returns cosine similarity matrix for cells' connectivity vectors."""
    X = mat.values
    cos_sim = cosine_similarity(X)
    return pd.DataFrame(cos_sim, index=mat.index, columns=mat.index)
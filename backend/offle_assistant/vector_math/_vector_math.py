import numpy as np


def cosine_similarity(A: np.array, B: np.array):
    """
    Cosine similarity utility.
    """
    if (len(A.shape) == 1) and (len(B.shape) == 1) and (A.size == B.size):
        cosine_similarity = np.dot(A, B) / (
            np.linalg.norm(A) * np.linalg.norm(B)
        )
    else:
        print(
            "Cosine similarity calculates similarity between two vectors "
            "of the same size. "
            f"These two values are size {A.size}, and {B.size}"
        )

    return cosine_similarity


def euclidean_distance(A: np.array, B: np.array):
    euclidean_distance = np.linalg.norm(A - B)
    return euclidean_distance

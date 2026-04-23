import math
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

# Load a small, CPU‑friendly transformer
# all-MiniLM-L6-v2 is ~22M params and runs fine on CPU
# Load a small, CPU‑friendly transformer
# all-MiniLM-L6-v2 is ~22M params and runs fine on CPU
_model = None
_APPROACH_EMB = None

# Define a small set of canonical approaches.
# You can adjust these labels and descriptions as needed.
_APPROACH_DESCRIPTIONS: Dict[str, str] = {
    "brute_force": "Try every possible option directly (often nested loops) without pruning or optimization.",
    "two_pointers": "Use two indices moving toward each other or along the array/string to shrink the search space.",
    "sliding_window": "Maintain a window over the data and move boundaries while preserving an invariant (often for subarray/string problems).",
    "prefix_sum": "Precompute cumulative sums so range queries / subarray sums can be answered efficiently.",
    "modified_binary_search": "Use binary search with an adjustment/variant (lower/upper bound, searching on answer space, etc.).",
    "backtracking": "Build solutions incrementally with recursion, try choices, and undo (track state) to explore possibilities.",
    "dynamic_programming": "Use DP with states and transitions (memoization or bottom-up table) to solve overlapping subproblems.",
    "hash_map": "Use a hash table/map/dictionary to store key-value pairs for O(1) lookup and efficient counting or grouping.",
}

_APPROACH_KEYS: List[str] = list(_APPROACH_DESCRIPTIONS.keys())

def _get_model():
    global _model, _APPROACH_EMB
    if _model is None:
        print("⏳ Loading SentenceTransformer model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Pre‑compute embeddings for the approach descriptions once at load time
        _APPROACH_TEXTS = [_APPROACH_DESCRIPTIONS[k] for k in _APPROACH_KEYS]
        _APPROACH_EMB = _model.encode(_APPROACH_TEXTS, normalize_embeddings=True)
        print("✅ SentenceTransformer loaded")
    return _model, _APPROACH_EMB


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # a and b are assumed to be L2‑normalized 1D vectors
    return float(np.dot(a, b))


def get_code_embedding(code: str) -> List[float]:
    """
    Returns a dense embedding vector for the code using a small transformer.

    This is a drop‑in replacement for the old CodeBERT-based get_code_embedding.
    """
    model, _ = _get_model()
    emb = model.encode(code, normalize_embeddings=False)
    return emb.astype(float).tolist()


def get_embedding_summary(embedding: List[float]) -> str:
    """
    Produce a lightweight textual summary of the code embedding by
    computing similarity to our canonical approaches and listing top matches.
    """
    # Normalize input embedding for cosine similarity
    vec = np.array(embedding, dtype=float)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return "Embedding summary not available (zero vector)."
    vec_norm = vec / norm

    _, approach_emb = _get_model()

    sims = [_cosine_similarity(vec_norm, appr_emb) for appr_emb in approach_emb]
    sims = np.array(sims)

    # Get top-3 approaches
    top_k = min(3, len(_APPROACH_KEYS))
    top_indices = sims.argsort()[::-1][:top_k]

    summary_lines = []
    for idx in top_indices:
        key = _APPROACH_KEYS[idx]
        score = sims[idx]
        percent = round(max(0.0, min(1.0, (score + 1.0) / 2.0)) * 100.0, 2)  # map [-1,1] -> [0,100]
        summary_lines.append(f"{key.replace('_', ' ').title()}: {percent}% similarity")

    if not summary_lines:
        return "Embedding summary not available."

    return "Top approach signals based on embedding:\n" + "\n".join(summary_lines)


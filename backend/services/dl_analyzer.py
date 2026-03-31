import math
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

# Load a small, CPU‑friendly transformer
# all-MiniLM-L6-v2 is ~22M params and runs fine on CPU
_model = SentenceTransformer("all-MiniLM-L6-v2")

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

# Pre‑compute embeddings for the approach descriptions once at import time
_APPROACH_KEYS: List[str] = list(_APPROACH_DESCRIPTIONS.keys())
_APPROACH_TEXTS: List[str] = [_APPROACH_DESCRIPTIONS[k] for k in _APPROACH_KEYS]
_APPROACH_EMB = _model.encode(_APPROACH_TEXTS, normalize_embeddings=True)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # a and b are assumed to be L2‑normalized 1D vectors
    return float(np.dot(a, b))


def get_code_embedding(code: str) -> List[float]:
    """
    Returns a dense embedding vector for the code using a small transformer.

    This is a drop‑in replacement for the old CodeBERT-based get_code_embedding.
    """
    emb = _model.encode(code, normalize_embeddings=False)
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

    sims = [_cosine_similarity(vec_norm, appr_emb) for appr_emb in _APPROACH_EMB]
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


# ─── Code Pattern Detection (Hybrid Approach) ───────────────────────────────
def _detect_code_patterns(code: str) -> Dict[str, float]:
    """
    Detect code patterns to supplement ML-based approach detection.
    Returns pattern scores (0-100) for each approach based on code structure.
    """
    code_lower = code.lower()
    patterns = {
        "brute_force": 0.0,
        "two_pointers": 0.0,
        "sliding_window": 0.0,
        "prefix_sum": 0.0,
        "modified_binary_search": 0.0,
        "backtracking": 0.0,
        "dynamic_programming": 0.0,
        "hash_map": 0.0,
    }

    import re

    # Brute Force: nested loops (for/while inside for/while)
    # Handle both Python (for x in y:) and Java (for (...) {...})
    python_nested = len(re.findall(r'for\s+.*?:\s*.*?for\s+', code_lower)) + \
                    len(re.findall(r'while\s+.*?:\s*.*?while\s+', code_lower))
    java_nested = len(re.findall(r'for\s*\([^)]*\)\s*\{[^}]*for\s*\(', code_lower)) + \
                  len(re.findall(r'while\s*\([^)]*\)\s*\{[^}]*while\s*\(', code_lower)) + \
                  len(re.findall(r'for\s*\([^)]*\)\s*\{[^}]*while\s*\(', code_lower)) + \
                  len(re.findall(r'while\s*\([^)]*\)\s*\{[^}]*for\s*\(', code_lower))
    
    nested_loop_count = python_nested + java_nested
    if nested_loop_count > 0:
        # Strong detection for brute force - nested loops are definitive
        patterns["brute_force"] = min(100, 70 + nested_loop_count * 20)

    # Two Pointers: look for patterns like "i++" or "j--" or "left++/right--"
    two_ptr_patterns = (
        len(re.findall(r'[ij]\s*[\+\-]{2}', code_lower)) +  # i++, j--
        len(re.findall(r'[ij]\s*[\+\-]=', code_lower)) +  # i+=, j-=
        len(re.findall(r'(left|right)\s*[\+\-]{2}', code_lower)) +  # left++, right--
        len(re.findall(r'(left|right)\s*[\+\-]=', code_lower)) +  # left+=, right-=
        len(re.findall(r'(left|right)\s*=\s*0', code_lower)) +  # left = 0, right = len
        len(re.findall(r'(left|right)\s*=\s*\w+\.length', code_lower))  # left = arr.length
    )
    if two_ptr_patterns > 2:
        patterns["two_pointers"] = min(100, 40 + two_ptr_patterns * 15)

    # Sliding Window: window, start, end patterns with loop
    if ('left' in code_lower or 'right' in code_lower or 'start' in code_lower or 'end' in code_lower or 'window' in code_lower) and \
       ('while' in code_lower or 'for' in code_lower) and \
       len(re.findall(r'(left|right|start|end|window)\s*[\+\-]', code_lower)) > 1:
        patterns["sliding_window"] = 60

    # HashMap / Hash Table: explicit hash map usage - STRONG DETECTION
    hashmap_detected = any(kw in code_lower for kw in ['hashmap', 'hash_map', 'hashset', 'hash_set', 'hashtable', 'hash_table', 'map<', 'set<', '.put(', '.get(', 'containskey', 'contains_key', 'map.put', 'map.get', 'map[', 'dict['])
    if hashmap_detected:
        # Strongly identify as HashMap - this is explicit code structure
        patterns["hash_map"] = 90

    # Prefix Sum: cumsum, sum, prefix patterns
    if any(kw in code_lower for kw in ['cumsum', 'prefix', 'precompute']) and 'sum' in code_lower:
        patterns["prefix_sum"] = 70

    # Modified Binary Search: binary search with adjustments
    if any(kw in code_lower for kw in ['binary', 'bsearch', 'mid', 'left', 'right']) and \
       ('while' in code_lower or 'for' in code_lower):
        patterns["modified_binary_search"] = 75

    # Backtracking: recursion with backtrack, dfs, helper functions
    if any(kw in code_lower for kw in ['backtrack', 'dfs', 'recursive', 'helper']) or \
       (len(re.findall(r'(def|void|int|boolean|string)\s+\w+\s*\(', code_lower)) > 1 and 'return' in code_lower):
        patterns["backtracking"] = 70

    # Dynamic Programming: dp array, memo, memoization, cache
    if any(kw in code_lower for kw in ['dp', 'memo', 'memoization', 'cache']) or \
       re.search(r'dp\[', code_lower) or re.search(r'memo\[', code_lower):
        patterns["dynamic_programming"] = 85

    return patterns


def predict_approach(code: str) -> Dict:
    """
    Hybrid approach detector combining ML embeddings + code pattern detection.

    Steps:
    1. Get ML-based approach scores from embeddings
    2. Detect code patterns (nested loops, stack usage, etc.)
    3. Combine both signals:
       - If ML confidence is high (>70%), trust ML
       - If ML confidence is medium (50-70%), use pattern detection to verify
       - If patterns are strong, boost that approach's score
    4. Return best approach with combined confidence

    Returns:
    - predicted_approach: str (human-readable approach name)
    - confidence: float (0-100, combined score)
    - all_scores: Dict[str, float] (individual scores per approach)
    """
    import sys
    
    # Step 1: ML-based scoring
    code_emb = _model.encode(code, normalize_embeddings=True)
    sims = [_cosine_similarity(code_emb, appr_emb) for appr_emb in _APPROACH_EMB]
    sims = np.array(sims)
    ml_scores = ((sims + 1.0) / 2.0) * 100.0
    
    # Step 2: Pattern-based scoring
    pattern_scores = _detect_code_patterns(code)
    pattern_scores_array = np.array([pattern_scores[key] for key in _APPROACH_KEYS])

    # Step 3: Hybrid combination
    ml_max = ml_scores.max()
    pattern_max = pattern_scores_array.max()
    
    # DEBUG LOGGING
    print("\n" + "="*70, file=sys.stderr)
    print("HYBRID APPROACH DETECTION DEBUG", file=sys.stderr)
    print("="*70, file=sys.stderr)
    print("\nML SCORES:", file=sys.stderr)
    for key, score in zip(_APPROACH_KEYS, ml_scores):
        print(f"  {key:25s}: {score:6.2f}", file=sys.stderr)
    
    print("\nPATTERN SCORES:", file=sys.stderr)
    for key, score in zip(_APPROACH_KEYS, pattern_scores_array):
        print(f"  {key:25s}: {score:6.2f}", file=sys.stderr)
    
    print(f"\nML Max: {ml_max:.2f}, Pattern Max: {pattern_max:.2f}", file=sys.stderr)
    
    # If patterns are very strong (>70), they likely indicate the true approach
    if pattern_max > 70:
        print("→ Using PATTERN DETECTION (pattern_max > 70): 0.4×ML + 0.6×pattern", file=sys.stderr)
        combined_scores = 0.4 * ml_scores + 0.6 * pattern_scores_array
    # If ML is very confident, weight it heavily
    elif ml_max > 75:
        print("→ Using ML CONFIDENT (ml_max > 75): 0.85×ML + 0.15×pattern", file=sys.stderr)
        combined_scores = 0.85 * ml_scores + 0.15 * pattern_scores_array
    # If patterns are detected, give them weight
    elif pattern_max > 50:
        print("→ Using BALANCED MODE (50 < pattern_max ≤ 70): 0.6×ML + 0.4×pattern", file=sys.stderr)
        combined_scores = 0.6 * ml_scores + 0.4 * pattern_scores_array
    # Default: mostly ML
    else:
        print("→ Using DEFAULT MODE: 0.75×ML + 0.25×pattern", file=sys.stderr)
        combined_scores = 0.75 * ml_scores + 0.25 * pattern_scores_array

    print("\nCOMBINED SCORES:", file=sys.stderr)
    for key, score in zip(_APPROACH_KEYS, combined_scores):
        print(f"  {key:25s}: {score:6.2f}", file=sys.stderr)

    # Step 4: Find best approach
    best_idx = int(combined_scores.argmax())
    best_key = _APPROACH_KEYS[best_idx]
    best_score = float(combined_scores[best_idx])
    
    print(f"\n✓ PREDICTED: {best_key.replace('_', ' ').title()} (confidence: {best_score:.2f})", file=sys.stderr)
    print("="*70 + "\n", file=sys.stderr)

    # Build all_scores dict with human-friendly names
    all_scores: Dict[str, float] = {}
    for key, score in zip(_APPROACH_KEYS, combined_scores):
        pretty = key.replace("_", " ").title()
        all_scores[pretty] = round(float(score), 2)

    predicted_readable = best_key.replace("_", " ").title()

    return {
        "predicted_approach": predicted_readable,
        "confidence": round(best_score, 2),
        "all_scores": all_scores,
    }
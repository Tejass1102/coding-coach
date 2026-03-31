"""
build_dataset.py

Offline dataset builder for Java-only code snippets labeled by approach.

Creates JSONL files from:
1) Seed examples in `training_data.py`
2) LeetCode CSV metadata (`Question_No`, `Topic_tags`, `Difficulty`)
3) A local clone of `cheehwatang/leetcode-java` under a `solutions/` directory

Output:
- `train.jsonl` (and optionally `val.jsonl` / `test.jsonl`)
- `dataset_stats.json`

Record format (one JSON per line):
{
  "code": "<full Java snippet>",
  "language": "java",
  "label": "<one of 10 internal label ids>",
  "problem_id": <int>,
  "difficulty": "<string or null>",
  "source": "seed_training_data" | "leetcode-java",
  "path": "<relative path to .java file or null>"
}
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


INTERNAL_LABELS: List[str] = [
    "brute_force",
    "two_pointers",
    "sliding_window",
    "prefix_sum",
    "monotonic_stack",
    "top_k_heap",
    "merge_intervals",
    "modified_binary_search",
    "backtracking",
    "dynamic_programming",
]

# Order matters for tie-breaking when multiple tags match.
LABEL_PRIORITY: List[str] = [
    "sliding_window",
    "two_pointers",
    "prefix_sum",
    "monotonic_stack",
    "top_k_heap",
    "merge_intervals",
    "modified_binary_search",
    "backtracking",
    "dynamic_programming",
    "brute_force",
]

TAG_TO_LABEL_RULES: List[Tuple[str, List[str]]] = [
    ("two_pointers", ["two pointers", "two pointer", "two_pointer", "two-pointers"]),
    ("sliding_window", ["sliding window", "sliding-window", "sliding_window"]),
    ("prefix_sum", ["prefix sum", "prefix_sum", "hash table", "hash map", "hashmap"]),
    ("monotonic_stack", ["monotonic stack", "monotonic_stack"]),
    ("top_k_heap", ["heap", "priority queue", "priority_queue", "top k", "top_k", "k-th smallest"]),
    ("merge_intervals", ["interval", "merge intervals", "merge interval"]),
    ("modified_binary_search", ["binary search", "lower bound", "upper bound", "bounds", "search on answer"]),
    ("backtracking", ["backtracking", "backtrack", "recursion", "recursive"]),
    ("dynamic_programming", ["dynamic programming", "dynamic_programming", "dp", "memoization", "memo"]),
    # Catch-all fallback to brute_force happens later.
]

SEED_OLD_LABEL_TO_NEW: Dict[str, str] = {
    "Brute Force": "brute_force",
    "Sliding Window": "sliding_window",
    "Dynamic Programming": "dynamic_programming",
    "Greedy": "merge_intervals",  # placeholder mapping; feel free to refine later
    "Binary Search": "modified_binary_search",
    "Divide & Conquer": "modified_binary_search",
    "Hash Map": "prefix_sum",  # placeholder mapping; keep dataset self-consistent with 10 labels
    "Two Pointers": "two_pointers",
}


def _norm(s: str) -> str:
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def parse_topic_tags(topic_tags_cell: str) -> List[str]:
    """
    Parses CSV cell like:
      "['Array', 'Two Pointers', 'Sliding Window']"
    into a list of tag strings.
    """
    if topic_tags_cell is None:
        return []
    cell = str(topic_tags_cell).strip()
    if not cell:
        return []

    # Typical case: a Python-literal list.
    try:
        tags = ast.literal_eval(cell)
        if isinstance(tags, list):
            return [str(t).strip() for t in tags if str(t).strip()]
    except Exception:
        pass

    # Fallback: split by commas and strip brackets/quotes.
    cell = cell.strip("[]")
    parts = [p.strip() for p in cell.split(",")]
    cleaned: List[str] = []
    for p in parts:
        p = p.strip().strip("'").strip('"')
        if p:
            cleaned.append(p)
    return cleaned


def tag_list_to_primary_label(tags: List[str]) -> str:
    """
    Maps a list of LeetCode `Topic_tags` into one of the 10 internal labels.
    """
    matched: List[str] = []
    for tag in tags:
        t = _norm(tag)
        for label, patterns in TAG_TO_LABEL_RULES:
            if any(_norm(pat) in t for pat in patterns):
                matched.append(label)
                break

    if not matched:
        return "brute_force"

    # Pick the highest-priority label.
    matched_unique = sorted(set(matched), key=lambda x: LABEL_PRIORITY.index(x))
    return matched_unique[0]


def label_from_path_heuristics(java_file_path: Path) -> Optional[str]:
    """
    Uses filename / directory name hints from the leetcode-java repo.
    """
    # Use normalized chunks from the full path.
    parts = [_norm(p) for p in java_file_path.parts]
    joined = " ".join(parts)
    filename = _norm(java_file_path.stem)

    keyword_checks: List[Tuple[str, List[str]]] = [
        ("two_pointers", ["two pointers", "two_pointer", "twopointers"]),
        ("sliding_window", ["sliding window", "sliding_window", "slidingwindow"]),
        ("prefix_sum", ["prefix sum", "prefix_sum", "prefixsum"]),
        ("monotonic_stack", ["monotonic stack", "monotonic_stack", "monotonicstack"]),
        ("top_k_heap", ["priority queue", "priority_queue", "heap", "top k", "top_k", "pq "]),
        ("merge_intervals", ["interval", "merge intervals", "mergeinterval", "merge_intervals"]),
        ("modified_binary_search", ["binary search", "binarysearch", "lower bound", "upper bound", "bound"]),
        ("backtracking", ["backtracking", "backtrack", "dfs backtrack"]),
        ("dynamic_programming", ["dynamic programming", "dynamic_programming", "dp", "memoization"]),
        ("brute_force", ["bruteforce", "brute force", "brute"]),
    ]

    for label, patterns in keyword_checks:
        if any(pat in joined or pat in filename for pat in patterns):
            return label
    return None


def looks_like_bruteforce(code: str) -> bool:
    """
    Very rough heuristic:
    - multiple `for (...)` loops
    - and no strong indicators of advanced patterns
    """
    for_count = len(re.findall(r"\bfor\s*\(", code))
    if for_count < 2:
        return False

    advanced_markers = [
        r"\bdp\s*\[",
        r"\bmemo",
        r"\bHashMap\b",
        r"\bHashSet\b",
        r"\bPriorityQueue\b",
        r"\bStack\b",
        r"monotonic",
        r"recursive",
        r"backtrack",
        r"dfs\s*\(",
        r"bfs\s*\(",
        r"while\s*\(",
    ]
    for pat in advanced_markers:
        if re.search(pat, code, flags=re.IGNORECASE):
            # `while` alone is common, so we only use it as part of marker checks
            if pat == r"while\s*\(":
                continue
            return False

    return True


def infer_label_for_java_file(
    *,
    java_file_path: Path,
    code: str,
    problem_id: Optional[int],
    problem_metadata: Dict[int, Dict],
) -> str:
    """
    Label assignment priority:
    1) filename/directory hints
    2) LeetCode CSV primary label for that problem_id
    3) brute_force fallback + nested loop heuristic
    """
    label_path = label_from_path_heuristics(java_file_path)
    problem_primary = None
    if problem_id is not None and problem_id in problem_metadata:
        problem_primary = problem_metadata[problem_id].get("primary_label")

    label = label_path or problem_primary or "brute_force"

    # If we didn't have a strong pattern label, allow nested-loop override.
    strong_labels = {
        "sliding_window",
        "two_pointers",
        "prefix_sum",
        "monotonic_stack",
        "top_k_heap",
        "merge_intervals",
        "modified_binary_search",
        "backtracking",
        "dynamic_programming",
    }
    if label not in strong_labels and looks_like_bruteforce(code):
        label = "brute_force"

    # If we *do* have brute_force from weak signals, improve it with nested-loop rule.
    if label == "brute_force" and not looks_like_bruteforce(code):
        # It's possible it's not brute force; we keep brute_force as fallback
        # rather than guessing another label.
        pass

    return label


def parse_problem_id_from_solution_path(java_file_path: Path) -> Optional[int]:
    """
    Assumes file path like:
      solutions/3. Longest Substring/SomeSolution.java
    and extracts leading integer `3`.
    """
    parent_folder_name = java_file_path.parent.name  # e.g. "3. Longest Substring"
    m = re.match(r"^\s*(\d+)\s*\.", parent_folder_name)
    if m:
        return int(m.group(1))
    # Some variants store it in parent.parent; try that too.
    pp = java_file_path.parent.parent.name
    m2 = re.match(r"^\s*(\d+)\s*\.", pp)
    if m2:
        return int(m2.group(1))
    return None


def sha1_text(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


def build_seed_rows() -> List[Dict]:
    """
    Converts `training_data.py` into JSONL rows in the new 10-label space.
    """
    script_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(script_dir))
    from training_data import data as seed_data  # type: ignore
    from training_data import LABEL_NAMES as old_label_names  # type: ignore

    rows: List[Dict] = []
    seen_hashes: set[str] = set()

    for code, old_label_idx in seed_data:
        old_label_name = old_label_names.get(int(old_label_idx))
        if old_label_name is None:
            continue
        new_label = SEED_OLD_LABEL_TO_NEW.get(old_label_name, "brute_force")

        h = sha1_text(code)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)

        rows.append(
            {
                "code": code,
                "language": "java",
                "label": new_label,
                "problem_id": None,
                "difficulty": None,
                "source": "seed_training_data",
                "path": None,
            }
        )

    return rows


def load_problem_metadata_from_csv(csv_path: Path) -> Dict[int, Dict]:
    """
    Loads CSV into:
      problem_id -> {difficulty, topic_tags, primary_label}
    """
    import csv as csvlib

    with csv_path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csvlib.DictReader(f)
        # Try to locate relevant columns.
        headers_lower = {h.lower(): h for h in reader.fieldnames or []}

        def get_col(*candidates: str) -> Optional[str]:
            for c in candidates:
                if c.lower() in headers_lower:
                    return headers_lower[c.lower()]
            return None

        col_qno = get_col("Question_No", "Question No", "Question_No.", "Question_Number", "Question_No ")
        col_topic = get_col("Topic_tags", "Topic Tags", "Topic_tag", "Topic_tags ")
        col_diff = get_col("Difficulty", "difficulty")

        if not col_qno or not col_topic:
            raise ValueError(f"CSV missing required columns. Found: {reader.fieldnames}")

        problem_metadata: Dict[int, Dict] = {}
        for row in reader:
            qno_cell = row.get(col_qno)
            if qno_cell is None:
                continue
            try:
                problem_id = int(str(qno_cell).strip())
            except Exception:
                continue

            difficulty = row.get(col_diff) if col_diff else None
            topic_tags_cell = row.get(col_topic)
            tags = parse_topic_tags(topic_tags_cell or "")
            primary_label = tag_list_to_primary_label(tags)

            problem_metadata[problem_id] = {
                "difficulty": str(difficulty).strip() if difficulty not in (None, "") else None,
                "topic_tags": tags,
                "primary_label": primary_label,
            }

    return problem_metadata


def maybe_clone_leetcode_java(repo_url: str, dest_path: Path) -> None:
    if dest_path.exists():
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Cloning {repo_url} into {dest_path} ...")
    subprocess.run(["git", "clone", "--depth", "1", repo_url, str(dest_path)], check=True)


def iter_leetcode_java_files(leetcode_java_root: Path) -> Iterable[Path]:
    """
    Walks a repo and yields all `.java` solution files under `solutions/`.
    """
    solutions_root = leetcode_java_root / "solutions"
    if not solutions_root.exists():
        return
        yield  # pragma: no cover

    for root, _, files in os.walk(str(solutions_root)):
        root_path = Path(root)
        for fn in files:
            if fn.endswith(".java"):
                yield root_path / fn


def write_jsonl(path: Path, rows: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def compute_dataset_stats(rows: List[Dict]) -> Dict:
    label_counts: Counter = Counter(r["label"] for r in rows)
    sample_lens = [len(r.get("code") or "") for r in rows]
    avg_len = (sum(sample_lens) / len(sample_lens)) if sample_lens else 0.0
    return {
        "num_samples": len(rows),
        "label_counts": dict(label_counts),
        "avg_code_chars": round(avg_len, 2),
    }


def spot_check_rows(rows: List[Dict], *, per_label: int, seed: int) -> Dict[str, List[Dict]]:
    """
    Prints a few representative examples per label so you can quickly verify mapping quality.
    Returns a structure that can be serialized if you want.
    """
    rng = random.Random(seed)
    by_label: Dict[str, List[Dict]] = defaultdict(list)
    for r in rows:
        by_label[str(r["label"])].append(r)

    picked: Dict[str, List[Dict]] = {}
    for label, items in by_label.items():
        if not items:
            continue
        rng.shuffle(items)
        picked[label] = items[:per_label]

    # Print (human-friendly).
    for label in sorted(picked.keys()):
        examples = picked[label]
        print(f"\nLabel `{label}`: showing {len(examples)} example(s)")
        for ex in examples:
            pid = ex.get("problem_id")
            diff = ex.get("difficulty")
            src = ex.get("source")
            path = ex.get("path")
            code_len = len(ex.get("code") or "")
            print(f"  - problem_id={pid} diff={diff} source={src} path={path} code_chars={code_len}")

    return picked


def split_rows_by_problem_id(
    rows: List[Dict],
    *,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> Dict[str, List[Dict]]:
    """
    Splits at `problem_id` granularity to reduce leakage.
    """
    # Rows with problem_id=None cannot be grouped reliably; always keep them in train.
    fixed_train: List[Dict] = []
    grouped: Dict[int, List[Dict]] = defaultdict(list)

    for r in rows:
        pid = r.get("problem_id")
        if pid is None:
            fixed_train.append(r)
        else:
            grouped[int(pid)].append(r)

    problem_ids = list(grouped.keys())
    rng = random.Random(seed)
    rng.shuffle(problem_ids)

    n = len(problem_ids)
    n_val = int(round(n * val_ratio))
    n_test = int(round(n * test_ratio))
    n_train = max(0, n - n_val - n_test)

    train_ids = set(problem_ids[:n_train])
    val_ids = set(problem_ids[n_train : n_train + n_val])
    test_ids = set(problem_ids[n_train + n_val : n_train + n_val + n_test])

    out = {"train": [], "val": [], "test": []}
    out["train"].extend(fixed_train)

    for pid in problem_ids:
        if pid in train_ids:
            out["train"].extend(grouped[pid])
        elif pid in val_ids:
            out["val"].extend(grouped[pid])
        elif pid in test_ids:
            out["test"].extend(grouped[pid])
        else:
            out["train"].extend(grouped[pid])

    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leetcode-csv", type=str, required=True, help="Path to Leetcode_Questions_updated CSV")
    ap.add_argument("--leetcode-java-path", type=str, default=None, help="Local leetcode-java repo path (optional)")
    ap.add_argument("--leetcode-java-clone", action="store_true", help="Clone leetcode-java if path missing")
    ap.add_argument("--leetcode-java-url", type=str, default="https://github.com/cheehwatang/leetcode-java")
    ap.add_argument("--output-dir", type=str, default="backend/datasets", help="Where to write train.jsonl / val.jsonl / test.jsonl")
    ap.add_argument("--max-code-chars", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-split", action="store_true", help="Write everything to train.jsonl only")
    ap.add_argument("--val-ratio", type=float, default=0.1)
    ap.add_argument("--test-ratio", type=float, default=0.1)
    ap.add_argument("--stats-out", type=str, default="dataset_stats.json")
    ap.add_argument("--spot-check-per-label", type=int, default=0, help="Print N examples per label (debugging)")
    args = ap.parse_args()

    csv_path = Path(args.leetcode_csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    # Clone or use existing repo.
    if args.leetcode_java_path:
        leetcode_java_root = Path(args.leetcode_java_path)
    else:
        leetcode_java_root = Path(__file__).resolve().parent / "vendor" / "leetcode-java"

    if not leetcode_java_root.exists():
        if args.leetcode_java_clone:
            maybe_clone_leetcode_java(args.leetcode_java_url, leetcode_java_root)
        else:
            raise FileNotFoundError(
                f"leetcode-java not found at {leetcode_java_root}. Provide --leetcode-java-path or use --leetcode-java-clone."
            )

    problem_metadata = load_problem_metadata_from_csv(csv_path)
    print(f"Loaded metadata for {len(problem_metadata)} problems from CSV")

    # Collect rows.
    seed_rows = build_seed_rows()
    print(f"Seed rows: {len(seed_rows)}")

    leetcode_rows: List[Dict] = []
    seen_hashes: set[str] = set(sha1_text(r["code"]) for r in seed_rows)

    for java_file in iter_leetcode_java_files(leetcode_java_root):
        try:
            code = java_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if not code.strip():
            continue
        if len(code) > args.max_code_chars:
            code = code[: args.max_code_chars]

        pid = parse_problem_id_from_solution_path(java_file)
        if pid is None:
            continue

        rel_path = str(java_file.relative_to(leetcode_java_root)) if java_file.is_relative_to(leetcode_java_root) else str(java_file)

        label = infer_label_for_java_file(
            java_file_path=java_file,
            code=code,
            problem_id=pid,
            problem_metadata=problem_metadata,
        )

        diff = problem_metadata.get(pid, {}).get("difficulty")

        h = sha1_text(code)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)

        leetcode_rows.append(
            {
                "code": code,
                "language": "java",
                "label": label,
                "problem_id": pid,
                "difficulty": diff,
                "source": "leetcode-java",
                "path": rel_path,
            }
        )

    all_rows = seed_rows + leetcode_rows
    print(f"Total rows: {len(all_rows)} (seed + leetcode-java)")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.no_split:
        train_rows = all_rows
        write_jsonl(out_dir / "train.jsonl", train_rows)
        stats = compute_dataset_stats(train_rows)
        (out_dir / args.stats_out).write_text(json.dumps(stats, indent=2), encoding="utf-8")
        print(f"Wrote {out_dir / 'train.jsonl'}")
        print(f"Stats: {out_dir / args.stats_out}")

        if args.spot_check_per_label > 0:
            spot_check_rows(train_rows, per_label=args.spot_check_per_label, seed=args.seed)
        return

    splits = split_rows_by_problem_id(all_rows, val_ratio=args.val_ratio, test_ratio=args.test_ratio, seed=args.seed)
    for split_name, split_rows in splits.items():
        write_jsonl(out_dir / f"{split_name}.jsonl", split_rows)
        print(f"Wrote {out_dir / f'{split_name}.jsonl'} ({len(split_rows)} rows)")

    # Write combined stats.
    stats_all = compute_dataset_stats(all_rows)
    stats_by_split = {k: compute_dataset_stats(v) for k, v in splits.items()}
    payload = {"all": stats_all, "by_split": stats_by_split}
    (out_dir / args.stats_out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Stats: {out_dir / args.stats_out}")

    if args.spot_check_per_label > 0:
        # Spot-check across the full dataset (labels should already be consistent).
        spot_check_rows(all_rows, per_label=args.spot_check_per_label, seed=args.seed)


if __name__ == "__main__":
    main()


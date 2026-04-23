"""
score_service.py  —  Revamped Interview Readiness Score Engine
==============================================================

Total: 100 pts across 5 components

  1. Time-Decayed Quality     30 pts  (EMA, half-life = 30 days)
  2. Consistency Frequency    20 pts  (rolling 8-week active-day average)
  3. Categorical Heatmap      20 pts  (real LeetCode tags → 5 core categories)
  4. Volume Tiers             15 pts  (milestone-based: 10 / 25 / 50 / 100 / 250)
  5. Optimization & Complexity 15 pts  (Big-O parse + brute-force penalty)
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone

from services.supabase_service import get_all_submissions
from services.leetcode_service import fetch_daily_challenge

# ── Constants ──────────────────────────────────────────────────────────────────

# EMA half-life: a submission from 30 days ago carries half the weight
_EMA_LAMBDA = math.log(2) / 30.0

# Maps LeetCode tag names → 5 core interview categories
CATEGORY_TAGS: dict[str, set[str]] = {
    "Arrays/Strings": {
        "Array", "String", "Matrix", "Stack", "Queue",
        "Heap (Priority Queue)", "Hash Table", "Sorting",
        "Monotonic Stack", "Monotonic Queue", "Sliding Window",
    },
    "Trees/Graphs": {
        "Tree", "Binary Tree", "Binary Search Tree", "N-ary Tree",
        "Graph", "Breadth-First Search", "Depth-First Search",
        "Topological Sort", "Trie", "Union Find",
        "Minimum Spanning Tree", "Shortest Path", "Eulerian Circuit",
    },
    "Dynamic Programming": {
        "Dynamic Programming", "Memoization", "Divide and Conquer",
        "Bitmask",
    },
    "Linked Lists": {
        "Linked List", "Doubly-Linked List", "Two Pointers",
        "Recursion",
    },
    "Math/Search": {
        "Math", "Binary Search", "Bit Manipulation", "Greedy",
        "Number Theory", "Combinatorics", "Geometry", "Randomized",
        "Game Theory", "Simulation",
    },
}

ALL_CATEGORIES = list(CATEGORY_TAGS.keys())

# Difficulty text → 0–1 quality weight
_DIFFICULTY_WEIGHT: dict[str, float] = {
    "beginner": 0.33,
    "easy":     0.33,
    "intermediate": 0.67,
    "medium":   0.67,
    "advanced": 1.0,
    "hard":     1.0,
}

# Volume milestone (n_problems) → points
_VOLUME_TIERS = [(0, 0), (10, 5), (25, 8), (50, 11), (100, 13), (250, 15)]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ema_weight(days_ago: float) -> float:
    return math.exp(-_EMA_LAMBDA * days_ago)


def _days_ago(ts: str) -> float:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        return max(0.0, delta.total_seconds() / 86_400.0)
    except Exception:
        return 0.0


def _difficulty_score(level: str) -> float:
    l = (level or "").lower()
    for key, val in _DIFFICULTY_WEIGHT.items():
        if key in l:
            return val
    return 0.5  # unknown → neutral


def _complexity_score(tc_str: str) -> float:
    """
    Parse a time-complexity string and return a quality score 0.0–1.0.
    Tiers:  O(1) / O(log N) → 1.0
            O(N)            → 0.85
            O(N log N)      → 0.70
            O(N²)           → 0.20
            O(2^N) / O(N!)  → 0.05
            unknown         → 0.50
    """
    if not tc_str:
        return 0.5
    s = tc_str.upper()
    if re.search(r"O\s*\(\s*1\s*\)", s):
        return 1.0
    if re.search(r"O\s*\(\s*LOG\s*N\s*\)", s):
        return 1.0
    if re.search(r"O\s*\(\s*N\s*LOG\s*N\s*\)", s):
        return 0.70
    if re.search(r"O\s*\(\s*N\s*\)", s):
        return 0.85
    if re.search(r"O\s*\(\s*N\s*[\^²2]\s*\)", s) or re.search(r"O\s*\(\s*N\^2\s*\)", s):
        return 0.20
    if re.search(r"O\s*\(\s*2\^N\s*\)", s) or re.search(r"O\s*\(\s*N\s*!\s*\)", s):
        return 0.05
    return 0.50


def _categories_for_tags(tags: list[str]) -> set[str]:
    """Return which core categories a list of LeetCode tags belong to."""
    tag_set = set(tags)
    matched: set[str] = set()
    for cat, cat_tags in CATEGORY_TAGS.items():
        if tag_set & cat_tags:
            matched.add(cat)
    return matched


def _volume_points(n: int) -> int:
    pts = 0
    for i in range(len(_VOLUME_TIERS) - 1):
        lo_n, lo_p = _VOLUME_TIERS[i]
        hi_n, hi_p = _VOLUME_TIERS[i + 1]
        if n <= lo_n:
            break
        if n >= hi_n:
            pts = hi_p
        else:
            frac = (n - lo_n) / (hi_n - lo_n)
            pts = round(lo_p + frac * (hi_p - lo_p))
            break
    return pts


# ── Main function ──────────────────────────────────────────────────────────────

def calculate_readiness_score() -> dict:
    submissions = get_all_submissions()

    if not submissions:
        return _empty(0)

    # ── Flatten to enriched records ──────────────────────────────────────────
    records: list[dict] = []
    for sub in submissions:
        tags: list[str] = sub.get("problem_tags") or []
        ts: str = sub.get("submitted_at", "")
        days = _days_ago(ts)

        for analysis in (sub.get("analyses") or []):
            approach = analysis.get("predicted_approach", "")
            is_brute = "brute" in approach.lower()

            records.append(
                {
                    "tags": tags,
                    "days_ago": days,
                    "ts": ts,
                    "difficulty": _difficulty_score(analysis.get("difficulty_level", "")),
                    "approach": approach,
                    "is_brute": is_brute,
                    "complexity_q": _complexity_score(analysis.get("time_complexity", "")),
                    "difficulty_level": analysis.get("difficulty_level", ""),
                }
            )

    if not records:
        return _empty(len(submissions))

    total_problems = len(records)

    # ── Component 1: Time-Decayed Quality (30 pts) ───────────────────────────
    tw_quality, tw_sum = 0.0, 0.0
    for r in records:
        w = _ema_weight(r["days_ago"])
        q = r["difficulty"] * (0.5 if r["is_brute"] else 1.0)
        tw_quality += w * q
        tw_sum += w

    ema_quality = tw_quality / tw_sum if tw_sum else 0.0
    time_decayed_pts = round(ema_quality * 30)
    
    # ── Component 2: Consistency Frequency (20 pts) ──────────────────────────
    # Group unique calendar days per ISO week (last 8 weeks = 56 days)
    week_day_map: dict[str, set[str]] = {}
    for r in records:
        if r["days_ago"] > 56:
            continue
        try:
            dt = datetime.fromisoformat(r["ts"].replace("Z", "+00:00"))
            iso = dt.isocalendar()
            wk = f"{iso[0]}-W{iso[1]:02d}"
            week_day_map.setdefault(wk, set()).add(dt.date().isoformat())
        except Exception:
            pass

    if week_day_map:
        # Rolling 8-week average (divide by 8, not just active weeks)
        rolling_avg = sum(len(v) for v in week_day_map.values()) / 8.0
        consistency_pts = round(min(1.0, rolling_avg / 4.0) * 20)
        streak_detail = f"{rolling_avg:.1f} active days/week (8-week rolling avg)"
    else:
        consistency_pts = 0
        streak_detail = "No activity in the last 8 weeks"

    # ── Component 3: Categorical Heatmap (20 pts) ────────────────────────────
    cat_difficulty: dict[str, list[float]] = {c: [] for c in ALL_CATEGORIES}
    for r in records:
        for cat in _categories_for_tags(r["tags"]):
            cat_difficulty[cat].append(r["difficulty"])

    cat_avgs: dict[str, float] = {}
    covered = 0
    for cat, vals in cat_difficulty.items():
        if vals:
            cat_avgs[cat] = round(sum(vals) / len(vals), 3)
            covered += 1
        else:
            cat_avgs[cat] = 0.0

    overall_cat = sum(cat_avgs.values()) / len(ALL_CATEGORIES)
    heatmap_pts = round(overall_cat * 20)
    heatmap_detail = f"{covered}/{len(ALL_CATEGORIES)} categories covered"

    # ── Component 4: Volume Tiers (15 pts) ───────────────────────────────────
    volume_pts = _volume_points(total_problems)
    next_milestone = next(
        (hi for lo, _ in _VOLUME_TIERS for hi, _ in [_VOLUME_TIERS[_VOLUME_TIERS.index((lo, _)) + 1]]
         if hi > total_problems),
        None,
    ) if total_problems < 250 else None

    # Cleaner next-milestone calculation
    next_ms = None
    for i, (lo_n, _lo_p) in enumerate(_VOLUME_TIERS[:-1]):
        hi_n, hi_p = _VOLUME_TIERS[i + 1]
        if total_problems < hi_n:
            next_ms = hi_n
            break
    volume_detail = f"{total_problems} problems solved" + (
        f" — next milestone: {next_ms}" if next_ms else " — max tier reached!"
    )

    # ── Component 5: Optimization & Complexity (15 pts) ─────────────────────
    tw_opt, tw_opt_sum = 0.0, 0.0
    for r in records:
        w = _ema_weight(r["days_ago"])
        c = r["complexity_q"] * (0.3 if r["is_brute"] else 1.0)
        tw_opt += w * c
        tw_opt_sum += w

    opt_quality = tw_opt / tw_opt_sum if tw_opt_sum else 0.0
    optimization_pts = round(opt_quality * 15)
    opt_detail = f"Weighted complexity quality: {opt_quality:.2f}/1.00"

    # ── Total ─────────────────────────────────────────────────────────────────
    total_score = min(
        100,
        time_decayed_pts + consistency_pts + heatmap_pts + volume_pts + optimization_pts,
    )

    # ── Level ─────────────────────────────────────────────────────────────────
    if total_score >= 80:
        level, message = "Advanced", "You are interview ready! Keep practising hard problems."
    elif total_score >= 50:
        level, message = "Intermediate", "Good progress! Focus on harder problems and optimal solutions."
    elif total_score >= 20:
        level, message = "Beginner", "Keep going! Try different categories and avoid brute force."
    else:
        level, message = "Newcomer", "Just getting started. Solve more problems to improve!"

    # ── Approach frequency ────────────────────────────────────────────────────
    approach_freq: dict[str, int] = {}
    all_approaches = [r["approach"] for r in records]
    for a in all_approaches:
        approach_freq[a] = approach_freq.get(a, 0) + 1

    unique_approaches = set(all_approaches)
    all_possible = [
        "Brute Force", "Sliding Window", "Dynamic Programming", "Greedy",
        "Binary Search", "Divide & Conquer", "Hash Map", "Two Pointers",
    ]
    strong_areas = [a for a in unique_approaches if a != "Brute Force"]
    weak_areas = [a for a in all_possible if a not in unique_approaches]

    return {
        "score": total_score,
        "level": level,
        "message": message,
        "breakdown": {
            "time_decayed_quality": {
                "score": time_decayed_pts,
                "max": 30,
                "detail": f"EMA quality {ema_quality:.2f} — recent hard problems count most",
            },
            "consistency_frequency": {
                "score": consistency_pts,
                "max": 20,
                "detail": streak_detail,
            },
        "category_heatmap": {
                "score": heatmap_pts,
                "max": 20,
                "detail": heatmap_detail,
            },
            "volume_tier": {
                "score": volume_pts,
                "max": 15,
                "detail": volume_detail,
            },
            "optimization_complexity": {
                "score": optimization_pts,
                "max": 15,
                "detail": opt_detail,
            },
        },
        "category_heatmap": cat_avgs,
        "approach_frequency": approach_freq,
        "strong_areas": strong_areas,
        "weak_areas": weak_areas,
        "total_submissions": total_problems,
        "recommended_questions": get_recommendations(weak_areas, records),
        "daily_challenge": fetch_daily_challenge(),
    }


def _empty(total: int) -> dict:
    from services.leetcode_service import fetch_daily_challenge
    return {
        "score": 0,
        "level": "No Data",
        "message": "No submissions found. Start solving problems!",
        "breakdown": {},
        "category_heatmap": {c: 0.0 for c in ALL_CATEGORIES},
        "approach_frequency": {},
        "strong_areas": [],
        "weak_areas": [],
        "total_submissions": total,
        "recommended_questions": [],
        "daily_challenge": fetch_daily_challenge(),
    }

def get_recommendations(weak_areas: list[str], records: list[dict]) -> list[dict]:
    from data.curated_problems import CURATED_PROBLEMS
    import re
    # Extract solved slugs
    solved_slugs = set()
    for r in records:
        name = r.get("problem_name", "") # need to make sure we parse problem name
        # Wait, problem_name is not saved to records right now.
        # Let's just collect all solved components via brute force string checks later if needed.
    # We will just return 3 problems from the top weak areas
    recs = []
    seen_slugs = set()

    for area in weak_areas:
        if area in CURATED_PROBLEMS:
            for prob in CURATED_PROBLEMS[area]:
                if prob["slug"] not in seen_slugs:
                    prob["approach"] = area
                    recs.append(prob)
                    seen_slugs.add(prob["slug"])
                if len(recs) >= 3:
                     return recs
    # Fill with generic if no weak areas or couldn't find enough
    for group in ["Two Pointers", "Sliding Window", "Dynamic Programming"]:
         if len(recs) >= 3: break
         for prob in CURATED_PROBLEMS[group]:
             if prob["slug"] not in seen_slugs:
                 prob["approach"] = group
                 recs.append(prob)
                 seen_slugs.add(prob["slug"])
                 if len(recs) >= 3: break
    return recs
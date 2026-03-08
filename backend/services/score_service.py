from services.supabase_service import get_all_submissions
from datetime import datetime, timezone


def calculate_readiness_score() -> dict:
    """
    Pulls all submissions from Supabase
    Calculates interview readiness score out of 100
    """
    submissions = get_all_submissions()

    if not submissions:
        return {
            "score": 0,
            "level": "No Data",
            "message": "No submissions found. Start solving problems!",
            "breakdown": {},
            "weak_areas": [],
            "strong_areas": [],
            "total_submissions": 0
        }

    # Extract all analyses
    analyses = []
    for sub in submissions:
        if sub.get("analyses"):
            for analysis in sub["analyses"]:
                analysis["problem_name"] = sub["problem_name"]
                analysis["submitted_at"] = sub["submitted_at"]
                analyses.append(analysis)

    if not analyses:
        return {
            "score": 0,
            "level": "No Data",
            "message": "Submissions found but no analyses yet.",
            "breakdown": {},
            "weak_areas": [],
            "strong_areas": [],
            "total_submissions": len(submissions)
        }

    # ── Score Component 1: Approach Variety (25 pts) ──────────
    all_approaches = [a["predicted_approach"] for a in analyses]
    unique_approaches = set(all_approaches)
    total_possible_approaches = 6
    variety_score = round(
        (len(unique_approaches) / total_possible_approaches) * 25
    )

    # ── Score Component 2: Difficulty Progress (25 pts) ───────
    difficulty_map = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    difficulty_scores = []
    for a in analyses:
        level = a.get("difficulty_level", "").lower()
        for key in difficulty_map:
            if key in level:
                difficulty_scores.append(difficulty_map[key])
                break

    if difficulty_scores:
        avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)
        # Scale: avg 1.0 = 8pts, avg 2.0 = 17pts, avg 3.0 = 25pts
        difficulty_score = round((avg_difficulty / 3.0) * 25)
    else:
        difficulty_score = 0

    # ── Score Component 3: Consistency (20 pts) ───────────────
    total_problems = len(analyses)
    # Scale: 1 problem = 2pts, 5 = 10pts, 10+ = 20pts
    consistency_score = min(20, round(total_problems * 2))

    # ── Score Component 4: Optimization Awareness (20 pts) ────
    # Check if student is solving problems with better approaches over time
    # High confidence brute force on easy problems = low awareness
    # Variety of non-brute-force approaches = high awareness
    non_brute_force = [
        a for a in analyses
        if a["predicted_approach"] != "Brute Force"
    ]
    if total_problems > 0:
        optimization_ratio = len(non_brute_force) / total_problems
        optimization_score = round(optimization_ratio * 20)
    else:
        optimization_score = 0

    # ── Score Component 5: Volume (10 pts) ────────────────────
    volume_score = min(10, total_problems)

    # ── Total Score ───────────────────────────────────────────
    total_score = (
        variety_score +
        difficulty_score +
        consistency_score +
        optimization_score +
        volume_score
    )
    total_score = min(100, total_score)

    # ── Determine Level ───────────────────────────────────────
    if total_score >= 80:
        level = "Advanced"
        message = "You are interview ready! Keep practicing hard problems."
    elif total_score >= 50:
        level = "Intermediate"
        message = "Good progress! Focus on harder problems and optimization."
    elif total_score >= 20:
        level = "Beginner"
        message = "Keep going! Try different problem types and approaches."
    else:
        level = "Newcomer"
        message = "Just getting started. Solve more problems to improve!"

    # ── Approach Frequency ────────────────────────────────────
    approach_frequency = {}
    for approach in all_approaches:
        approach_frequency[approach] = approach_frequency.get(approach, 0) + 1

    # ── Strong and Weak Areas ─────────────────────────────────
    all_possible = [
        "Brute Force", "Sliding Window", "Dynamic Programming",
        "Greedy", "Binary Search", "Divide & Conquer"
    ]
    strong_areas = [a for a in unique_approaches if a != "Brute Force"]
    weak_areas = [a for a in all_possible if a not in unique_approaches]

    return {
        "score": total_score,
        "level": level,
        "message": message,
        "breakdown": {
            "approach_variety": {
                "score": variety_score,
                "max": 25,
                "detail": f"{len(unique_approaches)}/{total_possible_approaches} approaches used"
            },
            "difficulty_progress": {
                "score": difficulty_score,
                "max": 25,
                "detail": f"Average difficulty: {avg_difficulty:.1f}/3.0" if difficulty_scores else "No data"
            },
            "consistency": {
                "score": consistency_score,
                "max": 20,
                "detail": f"{total_problems} problems solved"
            },
            "optimization_awareness": {
                "score": optimization_score,
                "max": 20,
                "detail": f"{len(non_brute_force)}/{total_problems} non-brute-force solutions"
            },
            "volume": {
                "score": volume_score,
                "max": 10,
                "detail": f"{total_problems} total submissions"
            }
        },
        "approach_frequency": approach_frequency,
        "strong_areas": strong_areas,
        "weak_areas": weak_areas,
        "total_submissions": total_problems
    }
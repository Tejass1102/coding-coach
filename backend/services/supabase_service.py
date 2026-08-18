from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("✅ Supabase connected")


def save_submission(problem_name: str, language: str, code: str, user_id: str, problem_tags: list = None) -> str:
    # Delete any previous submission for the same problem by the same user
    # so only the latest attempt is kept per user
    supabase.table("submissions").delete()\
        .eq("problem_name", problem_name)\
        .eq("user_id", user_id)\
        .execute()

    result = supabase.table("submissions").insert({
        "problem_name": problem_name,
        "language": language,
        "code": code,
        "user_id": user_id,
        "problem_tags": problem_tags or []
    }).execute()
    return result.data[0]["id"]


def save_analysis(
    submission_id: str,
    approach_detection: dict,
    analysis: dict,
    embedding_summary: str
) -> str:
    result = supabase.table("analyses").insert({
        "submission_id": submission_id,
        "predicted_approach": approach_detection["predicted_approach"],
        "confidence": approach_detection["confidence"],
        "all_scores": approach_detection["all_scores"],
        "approach_explanation": analysis["approach_explanation"],
        "time_complexity": analysis["time_complexity"],
        "space_complexity": analysis["space_complexity"],
        "optimization_tips": analysis["optimization_tips"],
        "good_practices": analysis["good_practices"],
        "difficulty_level": analysis["difficulty_level"]
    }).execute()
    return result.data[0]["id"]


def get_all_submissions(user_id: str) -> list:
    result = supabase.table("submissions")\
        .select("*, analyses(*)")\
        .eq("user_id", user_id)\
        .order("submitted_at", desc=True)\
        .execute()
    return result.data


def get_submission_by_id(submission_id: str, user_id: str) -> dict:
    result = supabase.table("submissions")\
        .select("*, analyses(*)")\
        .eq("id", submission_id)\
        .eq("user_id", user_id)\
        .execute()
    return result.data[0] if result.data else None
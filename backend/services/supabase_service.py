from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("✅ Supabase connected")


def save_submission(problem_name: str, language: str, code: str) -> str:
    # Delete any previous submission for the same problem so only the latest is kept
    supabase.table("submissions").delete().eq("problem_name", problem_name).execute()

    result = supabase.table("submissions").insert({
        "problem_name": problem_name,
        "language": language,
        "code": code
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


def get_all_submissions() -> list:
    result = supabase.table("submissions")\
        .select("*, analyses(*)")\
        .order("submitted_at", desc=True)\
        .execute()
    return result.data


def get_submission_by_id(submission_id: str) -> dict:
    result = supabase.table("submissions")\
        .select("*, analyses(*)")\
        .eq("id", submission_id)\
        .execute()
    return result.data[0] if result.data else None
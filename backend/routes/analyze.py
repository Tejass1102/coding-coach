from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.dl_analyzer import get_code_embedding, get_embedding_summary
from services.classifier_service import predict_approach
from services.gemini_service import analyze_with_gemini
from services.supabase_service import save_submission, save_analysis
from services.score_service import calculate_readiness_score
from services.gemini_service import get_verdict_tips, predict_correctness
from services.leetcode_service import fetch_problem_metadata, fetch_daily_challenge

router = APIRouter()

class CodeInput(BaseModel):
    code: str
    language: str = "python"
    problem_name: str = "Unknown Problem"

@router.post("/analyze")
def analyze_code(input: CodeInput):
    if not input.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if len(input.code) > 10000:
        raise HTTPException(status_code=400, detail="Code too long")

    # Step 1 — CodeBERT embedding
    embedding = get_code_embedding(input.code)
    summary = get_embedding_summary(embedding)

    # Step 2 — Approach classification
    approach = predict_approach(input.code)

    # Step 3 — Groq analysis
    analysis = analyze_with_gemini(
        code=input.code,
        language=input.language,
        approach=approach["predicted_approach"],
        confidence=approach["confidence"],
        all_scores=approach["all_scores"]
    )

    # Step 4 — Fetch LeetCode tags & similar questions, then save to Supabase
    metadata = fetch_problem_metadata(input.problem_name)
    problem_tags = metadata.get("tags", [])
    similar_questions = metadata.get("similar_questions", [])
    
    submission_id = save_submission(
        problem_name=input.problem_name,
        language=input.language,
        code=input.code,
        problem_tags=problem_tags
    )
    analysis_id = save_analysis(
        submission_id=submission_id,
        approach_detection=approach,
        analysis=analysis,
        embedding_summary=summary
    )

    # Fetch daily challenge for extension payload
    daily_challenge = fetch_daily_challenge()

    return {
        "submission_id": submission_id,
        "analysis_id": analysis_id,
        "problem_name": input.problem_name,
        "language": input.language,
        "approach_detection": approach,
        "analysis": analysis,
        "embedding_summary": summary,
        "similar_questions": similar_questions,
        "daily_challenge": daily_challenge,
        "message": "✅ Analysis saved and complete"
    }


@router.get("/history")
def get_history():
    from services.supabase_service import get_all_submissions
    submissions = get_all_submissions()
    return {
        "total": len(submissions),
        "submissions": submissions
    }


@router.get("/submission/{submission_id}")
def get_submission(submission_id: str):
    from services.supabase_service import get_submission_by_id
    submission = get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.get("/score")
def get_readiness_score():
    """
    Calculates and returns interview readiness score
    based on all past submissions
    """
    score_data = calculate_readiness_score()
    return score_data

@router.post("/analyze-only")
def analyze_code_only(input: CodeInput):
    """
    Analyzes code without saving to database
    Used for auto-analyze feature
    """
    if not input.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if len(input.code) > 10000:
        raise HTTPException(status_code=400, detail="Code too long")

    embedding = get_code_embedding(input.code)
    summary = get_embedding_summary(embedding)
    approach = predict_approach(input.code)
    analysis = analyze_with_gemini(
        code=input.code,
        language=input.language,
        approach=approach["predicted_approach"],
        confidence=approach["confidence"],
        all_scores=approach["all_scores"]
    )

    metadata = fetch_problem_metadata(input.problem_name)
    similar_questions = metadata.get("similar_questions", [])
    daily_challenge = fetch_daily_challenge()

    return {
        "problem_name": input.problem_name,
        "language": input.language,
        "embedding_summary": summary,
        "approach_detection": approach,
        "analysis": analysis,
        "similar_questions": similar_questions,
        "daily_challenge": daily_challenge,
        "saved": False,
        "message": "✅ Analysis complete (not saved)"
    }


@router.post("/save-submission")
def save_submission_endpoint(input: CodeInput):
    """
    Saves submission to database explicitly
    Called when student clicks Save button
    """
    if not input.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    embedding = get_code_embedding(input.code)
    summary = get_embedding_summary(embedding)
    approach = predict_approach(input.code)
    analysis = analyze_with_gemini(
        code=input.code,
        language=input.language,
        approach=approach["predicted_approach"],
        confidence=approach["confidence"],
        all_scores=approach["all_scores"]
    )

    metadata = fetch_problem_metadata(input.problem_name)
    problem_tags = metadata.get("tags", [])
    similar_questions = metadata.get("similar_questions", [])
    
    submission_id = save_submission(
        problem_name=input.problem_name,
        language=input.language,
        code=input.code,
        problem_tags=problem_tags
    )
    analysis_id = save_analysis(
        submission_id=submission_id,
        approach_detection=approach,
        analysis=analysis,
        embedding_summary=summary
    )

    daily_challenge = fetch_daily_challenge()

    return {
        "submission_id": submission_id,
        "analysis_id": analysis_id,
        "problem_name": input.problem_name,
        "language": input.language,
        "embedding_summary": summary,
        "approach_detection": approach,
        "analysis": analysis,
        "similar_questions": similar_questions,
        "daily_challenge": daily_challenge,
        "saved": True,
        "message": "✅ Analysis saved successfully"
    }

# ── ADD THIS at the bottom of routes/analyze.py ──

class VerdictRequest(BaseModel):
    code: str
    language: str
    problem_name: str
    verdict: str

@router.post("/analyze-verdict")
async def analyze_verdict(request: VerdictRequest):
    try:
        result = await get_verdict_tips(
            request.code,
            request.language,
            request.problem_name,
            request.verdict
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PreCheckRequest(BaseModel):
    code: str
    language: str
    problem_name: str

@router.post("/pre-check")
async def pre_check_solution(request: PreCheckRequest):
    """
    Uses Groq to predict if the solution is correct BEFORE running on LeetCode.
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    try:
        result = await predict_correctness(
            request.code,
            request.language,
            request.problem_name,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.codebert_service import get_code_embedding, get_embedding_summary
from services.classifier_service import predict_approach
from services.gemini_service import analyze_with_gemini
from services.supabase_service import save_submission, save_analysis
from services.score_service import calculate_readiness_score

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
        approach=approach["predicted_approach"],
        confidence=approach["confidence"],
        all_scores=approach["all_scores"]
    )

    # Step 4 — Save to Supabase
    submission_id = save_submission(
        problem_name=input.problem_name,
        language=input.language,
        code=input.code
    )
    analysis_id = save_analysis(
        submission_id=submission_id,
        approach_detection=approach,
        analysis=analysis,
        embedding_summary=summary
    )

    return {
        "submission_id": submission_id,
        "analysis_id": analysis_id,
        "problem_name": input.problem_name,
        "language": input.language,
        "embedding_summary": summary,
        "approach_detection": approach,
        "analysis": analysis,
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
        approach=approach["predicted_approach"],
        confidence=approach["confidence"],
        all_scores=approach["all_scores"]
    )

    return {
        "problem_name": input.problem_name,
        "language": input.language,
        "embedding_summary": summary,
        "approach_detection": approach,
        "analysis": analysis,
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
        approach=approach["predicted_approach"],
        confidence=approach["confidence"],
        all_scores=approach["all_scores"]
    )

    submission_id = save_submission(
        problem_name=input.problem_name,
        language=input.language,
        code=input.code
    )
    analysis_id = save_analysis(
        submission_id=submission_id,
        approach_detection=approach,
        analysis=analysis,
        embedding_summary=summary
    )

    return {
        "submission_id": submission_id,
        "analysis_id": analysis_id,
        "problem_name": input.problem_name,
        "language": input.language,
        "embedding_summary": summary,
        "approach_detection": approach,
        "analysis": analysis,
        "saved": True,
        "message": "✅ Analysis saved successfully"
    }

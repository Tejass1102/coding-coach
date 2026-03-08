from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.codebert_service import get_code_embedding, get_embedding_summary
from services.classifier_service import predict_approach
from services.gemini_service import analyze_with_gemini

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

    # Step 2 — Approach classification (DL model)
    approach = predict_approach(input.code)

    # Step 3 — Gemini analysis (human readable tips)
    gemini_analysis = analyze_with_gemini(
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
        "analysis": gemini_analysis,
        "message": "✅ Full analysis complete"
    }

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fraud_analyzer.duplicate import detect_duplicate_claim
from fraud_analyzer.name_matching import name_similarity_score
from fraud_analyzer.rules import build_claim_rule_summary

app = FastAPI(title="AI Detective API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClaimRequest(BaseModel):
    claim_id: str = "CLM-0001"
    policy_holder_name: str
    claimant_name: str | None = None
    claim_date: str
    policy_start_date: str
    policy_end_date: str
    billed_amount: float = 0.0
    claimed_amount: float = 0.0


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "AI Detective", "environment": "local-dev"}


@app.get("/api/providers")
def providers() -> dict[str, Any]:
    return {
        "providers": [
            "OpenRouter",
            "Groq",
            "Gemini",
            "Ollama",
        ]
    }


@app.post("/api/analyze")
def analyze_claim(payload: ClaimRequest) -> dict[str, Any]:
    claim_data = payload.model_dump()
    summary = build_claim_rule_summary(claim_data)
    comparison_name = payload.claimant_name or payload.policy_holder_name
    summary["name_similarity_score"] = name_similarity_score(payload.policy_holder_name, comparison_name)
    summary["duplicate_signal"] = detect_duplicate_claim(claim_data, [])
    return {
        "success": True,
        "signals": summary,
        "claim_id": payload.claim_id,
    }


@app.post("/api/analyze-file")
async def analyze_uploaded_file(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1", errors="ignore")
    return {
        "success": True,
        "filename": file.filename,
        "preview": text[:800],
        "message": "File upload accepted. Attach OCR/indexing pipeline next.",
    }

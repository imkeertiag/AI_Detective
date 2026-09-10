from __future__ import annotations

from typing import Any

from .name_matching import name_similarity_score


def detect_duplicate_claim(claim: dict[str, Any], historical_claims: list[dict[str, Any]]) -> dict[str, Any]:
    current_name = claim.get("policy_holder_name") or claim.get("claimant_name") or ""
    current_claim_id = str(claim.get("claim_id") or "")
    current_amount = float(claim.get("claimed_amount", 0) or 0)
    current_date = str(claim.get("claim_date") or "")

    for prior in historical_claims:
        prior_name = prior.get("policy_holder_name") or prior.get("claimant_name") or ""
        prior_claim_id = str(prior.get("claim_id") or "")
        prior_amount = float(prior.get("claimed_amount", 0) or 0)
        prior_date = str(prior.get("claim_date") or "")

        same_id = current_claim_id and current_claim_id == prior_claim_id
        same_name = name_similarity_score(current_name, prior_name) >= 0.9
        similar_amount = abs(current_amount - prior_amount) <= max(5000.0, 0.05 * max(current_amount, prior_amount))
        same_date = current_date and current_date == prior_date

        if same_id or (same_name and similar_amount and same_date):
            return {
                "is_duplicate": True,
                "matched_claim_id": prior_claim_id,
                "match_score": 1.0,
            }

    return {
        "is_duplicate": False,
        "matched_claim_id": None,
        "match_score": 0.0,
    }

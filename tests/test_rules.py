from fraud_analyzer.duplicate import detect_duplicate_claim
from fraud_analyzer.name_matching import name_similarity_score
from fraud_analyzer.rules import compute_amount_variance_pct, is_claim_amount_inflated, policy_date_valid


def test_amount_variance_calculation():
    variance = compute_amount_variance_pct(550000, 350000)
    assert round(variance, 2) == 57.14
    assert is_claim_amount_inflated(550000, 350000) is True


def test_policy_date_validation():
    assert policy_date_valid("2023-01-01", "2024-12-31", "2024-02-01") is True
    assert policy_date_valid("2023-01-01", "2024-12-31", "2025-01-01") is False


def test_name_similarity():
    score = name_similarity_score("Rajesh Kumar Singh", "Rajesh K Singh")
    assert score > 0.8


def test_duplicate_detection():
    claim = {"claim_id": "CLM-0201", "claimant_name": "Rajesh Kumar Singh", "claimed_amount": 250000, "claim_date": "2024-02-09"}
    history = [{"claim_id": "CLM-0200", "claimant_name": "Rajesh K Singh", "claimed_amount": 249900, "claim_date": "2024-02-09"}]
    result = detect_duplicate_claim(claim, history)
    assert result["is_duplicate"] is True

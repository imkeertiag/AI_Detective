"""Insurance claim fraud analyzer MVP."""

from .rules import compute_amount_variance_pct, is_claim_amount_inflated, policy_date_valid
from .name_matching import name_similarity_score
from .duplicate import detect_duplicate_claim

__all__ = [
    "compute_amount_variance_pct",
    "is_claim_amount_inflated",
    "policy_date_valid",
    "name_similarity_score",
    "detect_duplicate_claim",
]

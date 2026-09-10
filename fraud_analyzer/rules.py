from __future__ import annotations

from datetime import date, datetime
from typing import Any


def parse_date(value: str | date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            continue
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def compute_amount_variance_pct(claimed_amount: float | int, billed_amount: float | int) -> float:
    billed_amount = float(billed_amount)
    claimed_amount = float(claimed_amount)
    if billed_amount <= 0:
        return 0.0
    return round(((claimed_amount - billed_amount) / billed_amount) * 100.0, 2)


def is_claim_amount_inflated(claimed_amount: float | int, billed_amount: float | int, threshold_pct: float = 15.0) -> bool:
    return compute_amount_variance_pct(claimed_amount, billed_amount) >= float(threshold_pct)


def policy_date_valid(policy_start: str | date | None, policy_end: str | date | None, claim_date: str | date | None) -> bool:
    start = parse_date(policy_start)
    end = parse_date(policy_end)
    claim = parse_date(claim_date)
    if start is None or end is None or claim is None:
        return False
    return start <= claim <= end


def build_claim_rule_summary(claim: dict[str, Any]) -> dict[str, Any]:
    claimed_amount = float(claim.get("claimed_amount", 0) or 0)
    billed_amount = float(claim.get("billed_amount", 0) or 0)
    variance_pct = compute_amount_variance_pct(claimed_amount, billed_amount)
    return {
        "amount_variance_pct": variance_pct,
        "is_amount_inflation": is_claim_amount_inflated(claimed_amount, billed_amount),
        "policy_valid": policy_date_valid(
            claim.get("policy_start_date"),
            claim.get("policy_end_date"),
            claim.get("claim_date"),
        ),
    }

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fraud_analyzer.data_generator import generate_claim_dataset
from fraud_analyzer.duplicate import detect_duplicate_claim
from fraud_analyzer.name_matching import name_similarity_score
from fraud_analyzer.rules import build_claim_rule_summary


def analyze_claim(claim: dict, history: list[dict] | None = None) -> dict:
    history = history or []
    summary = build_claim_rule_summary(claim)
    summary["name_similarity_score"] = name_similarity_score(
        claim.get("policy_holder_name"),
        claim.get("claimant_name") or claim.get("policy_holder_name"),
    )
    summary["duplicate_signal"] = detect_duplicate_claim(claim, history)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the fraud analyzer against a claim JSON file")
    parser.add_argument("--claim", type=str, default=None, help="Path to a claim JSON file")
    parser.add_argument("--generate", action="store_true", help="Generate demo synthetic data instead")
    args = parser.parse_args()

    if args.generate:
        dataset = generate_claim_dataset(count=25, fraud_rate=0.35, output_dir="./synthetic_data")
        print(json.dumps({"generated_records": len(dataset)}, indent=2))
        raise SystemExit(0)

    if not args.claim:
        sample_claim = {
            "claim_id": "CLM-0100",
            "policy_holder_name": "Rajesh Kumar Singh",
            "claimant_name": "Rajesh K Singh",
            "claim_date": "2024-02-10",
            "policy_start_date": "2023-01-01",
            "policy_end_date": "2024-12-31",
            "billed_amount": 350000,
            "claimed_amount": 550000,
        }
        print(json.dumps(analyze_claim(sample_claim), indent=2))
    else:
        path = Path(args.claim)
        claim = json.loads(path.read_text())
        print(json.dumps(analyze_claim(claim), indent=2))

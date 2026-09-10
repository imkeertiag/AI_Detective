from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from faker import Faker


@dataclass
class ClaimRecord:
    claim_id: str
    policy_holder_name: str
    hospital_name: str
    policy_start_date: str
    policy_end_date: str
    claim_date: str
    billed_amount: float
    claimed_amount: float
    diagnosis: str
    is_fraudulent: bool
    fraud_type: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


fake = Faker("en_IN")


def generate_claim_record(index: int, fraudulent: bool = False, duplicate_of: str | None = None) -> ClaimRecord:
    names = [
        "Rajesh Kumar Singh",
        "Rajeev Kumar Singh",
        "Rakesh K Singh",
        "Amit Sharma",
        "Suresh Verma",
        "Neha Gupta",
        "Priya Nair",
    ]
    hospitals = ["Apollo Hospital", "Fortis Hospital", "Medanta", "Tata Memorial", "Narayana Health"]
    diagnosis = ["Fracture Repair", "Knee Arthroscopy", "Cardiac Angioplasty", "Appendicitis", "Delivery Care"]

    base_name = random.choice(names)
    if fraudulent and random.random() < 0.5:
        base_name = base_name.replace("Rajesh", "Rajeeh") if "Rajesh" in base_name else base_name

    policy_start = fake.date_between(start_date="-3y", end_date="-1y")
    policy_end = fake.date_between(start_date=policy_start, end_date="+1y")
    claim_date = fake.date_between(start_date=policy_start, end_date=policy_end)

    billed_amount = random.randint(90000, 400000)
    claimed_amount = billed_amount
    fraud_type = None
    if fraudulent:
        if random.random() < 0.5:
            fraud_type = "amount_inflation"
            claimed_amount = int(billed_amount * random.uniform(1.35, 2.2))
        elif random.random() < 0.5:
            fraud_type = "date_mismatch"
            claimed_amount = billed_amount
            claim_date = fake.date_between(start_date="-4y", end_date=policy_start)
        else:
            fraud_type = "duplicate_claim"
            claimed_amount = billed_amount
            claim_date = fake.date_between(start_date=policy_start, end_date=policy_end)
            duplicate_of = f"CLM-{random.randint(1000, 9999)}"

    return ClaimRecord(
        claim_id=f"CLM-{index:05d}",
        policy_holder_name=base_name,
        hospital_name=random.choice(hospitals),
        policy_start_date=policy_start.isoformat(),
        policy_end_date=policy_end.isoformat(),
        claim_date=claim_date.isoformat(),
        billed_amount=float(billed_amount),
        claimed_amount=float(claimed_amount),
        diagnosis=random.choice(diagnosis),
        is_fraudulent=fraudulent,
        fraud_type=fraud_type,
    )


def generate_claim_dataset(count: int = 200, fraud_rate: float = 0.35, output_dir: str | Path = "./synthetic_data") -> list[dict]:
    records: list[dict] = []
    rng = random.Random(42)
    random.seed(42)
    total = int(count)
    for i in range(1, total + 1):
        fraudulent = rng.random() < fraud_rate
        record = generate_claim_record(i, fraudulent=fraudulent)
        records.append(record.to_dict())

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "claims.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    json_path = output_dir / "claims.json"
    json_path.write_text(json.dumps(records, indent=2))

    return records


if __name__ == "__main__":
    generate_claim_dataset()

from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fraud_analyzer.data_generator import generate_claim_dataset


def train_model(dataset_path: str | Path, model_path: str | Path) -> dict:
    path = Path(dataset_path)
    if not path.exists():
        records = generate_claim_dataset(count=500, fraud_rate=0.3, output_dir=Path("./synthetic_data"))
        df = pd.DataFrame(records)
    else:
        df = pd.read_csv(path)

    features = [
        "billed_amount",
        "claimed_amount",
        "amount_variance_pct",
        "policy_valid",
    ]
    df["amount_variance_pct"] = ((df["claimed_amount"] - df["billed_amount"]) / df["billed_amount"]).fillna(0) * 100
    df["policy_valid"] = 1

    X = df[features]
    y = df["is_fraudulent"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
    }

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as handle:
        pickle.dump(model, handle)

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a local fraud risk model")
    parser.add_argument("--dataset", default="./synthetic_data/claims.csv")
    parser.add_argument("--output", default="./ml/fraud_model.pkl")
    args = parser.parse_args()

    report = train_model(args.dataset, args.output)
    print(report)

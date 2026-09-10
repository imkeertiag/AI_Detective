# AI Detective

AI Detective is a fraud-detection and document-risk analysis platform for insurance, banking, loans, and real-estate workflows. It helps teams spot suspicious claims, unfair contract terms, and mismatches before approving or paying out.

Idea Description: A system that helps people to understand the contract clauses and highlighting risky/unfair terms also it can help banks, insurance companies, and real estate firms automatically detect suspicious/fraudulent claims and documents before processing them hence saving money and time.

How it works:
Person uploads rental agreement, loan contract, employment offer, insurance policy, pdf claims
Document AI extracts all text, dates, amounts names
Gemini analyses the document clause, dates, amounts and identifies:
Unfair terms
What could go wrong
compares it to market standards
Negotiable clauses
Checks whether dates, amounts make sense
Benefits the person by highlighting risky/unfair terms, and big firms analyse claims faster than usual

I would like to explain my idea with real life example:

The problem: 1. ICICI receives 50 insurance claims per day. Each claim needs 2-3 hours of manual review:
Is claimant really who they say?
Does claim date fall within policy period?
Do hospital charges match claimed amount?
Is medical history consistent?

My system flags it as:

FRAUD SIGNAL 1: Amount inflation
   Hospital bill: ₹3,50,000
   Claimed: ₹5,50,000
   Discrepancy: 57% OVERSTATED
   
FRAUD SIGNAL 2: Name inconsistency
   Policy: "Rajesh Kumar Singh"
   Hospital bill: "Rajesh K Singh"
   Bill witness: "Rajeesh Kumar Singh" = 3 different spellings (copy-paste from multiple sources)
   
FRAUD SIGNAL 3: Duplicate claim detected
   Same accident date (10-Feb-2024)
   Same hospital (Apollo Hospital, Delhi)
   Same bill total (₹3,50,000)
   Found 2 other similar claims from different "claimants"
   = RING FRAUD (organized claim duplication)

In similar way we can analyse corporate bonds and real estate frauds.

The project combines:
- Python FastAPI backend
- React.js frontend
- Google Cloud architecture patterns
- deterministic fraud checks
- optional AI-based document reasoning using OpenRouter/Gemini/Ollama

## Product idea

AI Detective analyzes uploaded claim and contract documents to find:
- amount inflation
- duplicate claims
- policy-date mismatches
- name inconsistencies
- unfair or risky legal language

This matches the project brief in the supplied document: a bank or insurer receives many claims a day and needs a faster, auditable first-pass review.

## Google Cloud direction

This repo is structured for an eventual Google Cloud deployment:
- Cloud Run for backend and frontend
- Cloud Storage for uploaded PDFs and processed artifacts
- BigQuery for historical claims and audit data
- Vertex AI / BigQuery ML for risk scoring
- Document AI or Gemini OCR extraction for ingestion
- Cloud Functions / Workflows for orchestration

## Current local MVP

This repository includes a working local MVP with:
- Python fraud rules
- duplicate detection logic
- name similarity scoring
- React UI for claim review
- FastAPI endpoint for analysis

## Project layout

```text
backend/               Python FastAPI service
  app/main.py           API endpoints for analysis
fraud_analyzer/        Core fraud detection logic
frontend/              React.js dashboard
ml/                    Sample ML model scripts
synthetic_data/         Demo claim data generation
```

## Quick start

```bash
cd /Users/keertiagarwal/Documents/AI Detective
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt
python -m pytest

# run backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# in another terminal, run frontend
cd frontend
npm install
npm run dev
```

## Frontend API

The React app calls the FastAPI backend at `/api/analyze`.

Example request:

```json
{
  "claim_id": "CLM-0001",
  "policy_holder_name": "Rajesh Kumar Singh",
  "claimant_name": "Rajesh K Singh",
  "claim_date": "2024-02-10",
  "policy_start_date": "2023-01-01",
  "policy_end_date": "2024-12-31",
  "billed_amount": 350000,
  "claimed_amount": 550000
}
```

## AI provider strategy

Free-tier AI providers can be plugged in through the project environment configuration.

Use OpenRouter, Gemini, Groq, or Ollama depending on your quota and availability.

## Main fraud signals implemented

- amount inflation percentage
- policy date validation
- name similarity checks
- duplicate claim detection with historical matching

## Next steps

1. Add PDF ingestion and OCR extraction
2. Integrate Google Cloud Storage + BigQuery
3. Add Vertex AI or BigQuery ML fraud scoring
4. Add document risk summaries and legal clause review
5. Deploy backend and frontend to Cloud Run

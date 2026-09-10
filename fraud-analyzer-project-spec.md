# Insurance Claim Document Fraud Analyzer — Project Spec

> Context file for GitHub Copilot / any AI coding assistant. Paste this into your repo root as `PROJECT.md` (or `.github/copilot-instructions.md`) so Copilot understands the architecture before you start generating code.

## 1. Problem statement

A bank/insurer (example: SBI-style use case) receives ~50 insurance claims/day. Each claim needs 2–3 hours of manual review to check:
- Is the claimant really who they say they are?
- Does the claim date fall within the policy period?
- Do hospital charges match the claimed amount?
- Is the medical history consistent across documents?

This project automates the first-pass triage of that review by flagging concrete fraud signals:
- **Amount inflation** — hospital bill vs. claimed amount discrepancy (e.g. bill ₹3,50,000 vs claimed ₹5,50,000 = 57% overstated)
- **Name inconsistency** — spelling variants across policy/bill/witness documents (e.g. "Rajesh Kumar Singh" vs "Rajesh K Singh" vs "Rajeesh Kumar Singh")
- **Duplicate claims** — same claim resubmitted or near-identical claim across records

## 2. Why this is not "just ask an LLM to read the claim"

A chatbot reading one document in isolation can't reliably do arithmetic at scale, has no memory of past claims, and its "fraud score" isn't measurable. This system's differentiation:

1. **Deterministic verification, not vibes** — amount variance %, date-range checks are computed by code, not asked of an LLM. The LLM only writes the human-readable explanation afterward.
2. **Cross-claim memory** — duplicate/fraud-ring detection requires querying a warehouse of past claims (BigQuery), which a chat session structurally cannot do.
3. **A trained, evaluated risk model** — an AutoML/BigQuery ML classifier scored against a labeled dataset gives a real precision/recall number, not a claimed one.

Pitch line: *"An LLM can read one document. This system remembers every claim it's ever seen, verifies the numbers deterministically, and gets more accurate over time."*

## 3. Budget: $300 Google Cloud free trial (90 days)

Cost strategy — **skip the expensive Document AI Custom Extractor tier entirely**:

| Component | Approach | Approx. cost |
|---|---|---|
| Text extraction from PDFs | Document AI **Enterprise OCR** ($1.50/1,000 pages) OR free **Tesseract/PyMuPDF** for dev/testing | Near-free for a few hundred docs |
| Field structuring (name, amount, dates) | **Gemini (`gemini-3.5-flash` or `gemini-3.5-flash-lite`)** multimodal prompt → structured JSON. Gemini accepts PDF input directly. | Pay-per-token, cheap at this volume |
| ~~Document AI Custom Extractor~~ | Deliberately **not used** — $30/1,000 pages + $0.05/hr hosting per deployed version is not worth it for a few hundred synthetic documents | Avoided |
| Risk scoring model | BigQuery ML or Vertex AI AutoML Tabular, trained once on Kaggle data | One-time training cost |
| Name matching | Phonetic (Soundex/Metaphone) + Levenshtein, algorithmic — **no cost, no training** | $0 |
| Report generation | Gemini, zero-shot on already-computed signals | Pay-per-token, cheap |
| Warehouse | BigQuery — free tier covers 1TB queries/month + 10GB storage | Likely $0 |
| Hosting | Cloud Run (scales to zero, pay-per-request) | Near-$0 when idle |

**Action items to protect the $300:**
- Set a **budget alert** in GCP Billing at $50/$100/$200 thresholds immediately after signup.
- **Undeploy/delete Document AI processor versions** between work sessions if you do use any custom processor — hosting bills per hour regardless of usage.
- Use `gemini-3.5-flash-lite` (not Pro-tier models) for high-volume calls during development; switch up only for the final demo if needed.
- Keep Cloud Run min-instances at 0 so nothing bills while you're not actively demoing.

## 4. Architecture

```
Upload (bundled claim PDF)
   → Cloud Storage (raw/)
   → Document AI Splitter/Classifier (or simple heuristic split for MVP)
   → Cloud Storage (split/) — one file per doc_type
   → Enterprise OCR (or Tesseract) → raw text
   → Gemini structured-extraction prompt → JSON fields
   → BigQuery (claims warehouse)
   → Rule engine (Cloud Run, Python) — amount variance, date validity
   → Name-matching service (Cloud Run) — phonetic + Levenshtein + embeddings
   → BigQuery SQL — duplicate/fraud-ring detection across historical claims
   → Risk model (BigQuery ML / AutoML) — fraud probability score
   → Gemini — synthesizes all signals into investigator-readable report
   → Frontend (Cloud Run + simple React/HTML) — shows flags + score
   → Looker Studio — aggregate dashboard on top of BigQuery
```

| Layer | GCP Service | AI/ML? |
|---|---|---|
| Storage | Cloud Storage | No |
| OCR | Document AI Enterprise OCR (or Tesseract for dev) | Yes (pretrained) |
| Field extraction | Gemini multimodal | Yes |
| Image forensics (stretch goal) | Vision API | Yes |
| Name matching | Custom code + `gemini-embedding-2` | Partially (embeddings) |
| Rule engine | Cloud Run (plain Python) | No — deterministic |
| Warehouse / duplicate detection | BigQuery | No — SQL |
| Risk scoring | BigQuery ML / Vertex AI AutoML Tabular | Yes — trained classifier |
| Report writing | Gemini | Yes |
| Orchestration | Cloud Workflows or Pub/Sub | No |
| Frontend | Cloud Run | No |
| Dashboard | Looker Studio | No |

## 5. Cloud Storage layout

```
gs://fraud-analyzer-claims/
  raw/{claim_id}/submission.pdf          ← original bundled scan, immutable
  split/{claim_id}/policy_doc.pdf
  split/{claim_id}/hospital_bill.pdf
  split/{claim_id}/id_proof.pdf
  split/{claim_id}/discharge_summary.pdf
  processed/{claim_id}/*.json            ← extracted structured fields
  synthetic/fraud/                       ← generated training/demo corpus (fraud-injected)
  synthetic/clean/                       ← generated training/demo corpus (clean)
```

## 6. Document type taxonomy

- `policy_document` — coverage dates, sum insured, policyholder name
- `hospital_bill` — itemized charges, total, hospital name/date
- `id_proof` — Aadhaar/PAN, government-record name spelling
- `discharge_summary` — diagnosis, admission/discharge dates, treating doctor
- `claim_form` — claimant-declared amount, claimant-declared name (baseline for comparison)

Every fraud signal is a cross-doc_type comparison: bill vs. claim_form for amount; id_proof vs. policy vs. bill for name; discharge_summary vs. policy for date range.

## 7. BigQuery manifest table (core schema)

```sql
CREATE TABLE claims.document_manifest (
  claim_id STRING,
  doc_type STRING,          -- policy_document | hospital_bill | id_proof | discharge_summary | claim_form
  gcs_uri_raw STRING,
  gcs_uri_split STRING,
  page_range STRING,
  extraction_status STRING, -- pending | done | failed
  extracted_fields JSON,
  ingested_at TIMESTAMP
);
```

Plus a `claims.claims_summary` table (one row per claim_id) joining extracted fields across doc types, and a `claims.fraud_signals` table logging computed signals per claim (amount_variance_pct, name_similarity_score, is_duplicate, risk_score) — this is what your audit trail and Looker dashboard read from.

## 8. Data sources

**Kaggle (for training the risk model — labeled tabular data):**
- "Healthcare Provider Fraud Detection Analysis" (Medicare-derived, provider/beneficiary/claims tables)
- "Healthcare Fraud Detection Dataset" (10,000 claims, ICD-10/CPT codes)
- "Insurance Claims Fraud Data" (adds employee/adjuster + vendor tables — useful for a collusion-detection stretch goal)
- "Enhanced Health Insurance Claims Dataset" (4,500 synthetic claims, for augmenting training data)

**BigQuery public dataset (for realistic feature distributions, not fraud labels):**
- `bigquery-public-data.cms_medicare` — real US CMS hospital/utilization/payment data. Good for realistic charge ranges and hospital metadata; has **no fraud labels**, so it's a feature-realism source, not a training-label source.

**Synthetic (generate yourself — no public dataset has labeled scanned Indian claim documents):**
- Script (Faker + reportlab/fpdf) generating ~200–500 hospital bills, policy docs, ID proofs with Indian names/formats
- Inject fraud into a known subset: amount inflation, name-spelling variants, duplicate submissions, out-of-policy-period dates
- Keep a ground-truth CSV of which are fraudulent and why — this is what lets you report your own pipeline's precision/recall

## 9. Build order

1. Load Kaggle datasets + CMS public dataset into BigQuery; align to a common schema
2. Train risk model (BigQuery ML / AutoML Tabular); record eval metrics (AUC, precision, recall)
3. Build synthetic document generator with fraud injection + ground-truth CSV
4. Ingestion: Cloud Storage bucket structure + Cloud Function trigger on upload
5. Extraction: Enterprise OCR (or Tesseract) → Gemini structured-JSON prompt
6. BigQuery manifest + claims_summary tables populated from extraction output
7. Rule engine (Cloud Run): amount variance, date-range validity
8. Name-matching service (Cloud Run): phonetic + Levenshtein + embeddings
9. BigQuery SQL: duplicate/fraud-ring detection across historical claims
10. Wire risk model scoring into the pipeline
11. Gemini report-writer: takes computed signals only, produces investigator summary
12. Orchestrate with Cloud Workflows/Pub/Sub
13. Frontend (Cloud Run) + Looker Studio dashboard
14. Write README with architecture diagram, eval numbers, and the differentiation pitch (Section 2 above)

## 10. What needs training vs. what doesn't

| Component | Training needed? |
|---|---|
| Risk-scoring model | Yes — Kaggle + CMS-derived features |
| Field extraction (via Gemini prompting) | No — zero-shot/few-shot prompt |
| Name matching | No — algorithmic + pretrained embeddings |
| Rule engine | No — hand-written logic |
| Report generation | No — zero-shot Gemini |

## 11. Repo structure suggestion

```
/ingestion         Cloud Function(s) for upload → split → OCR → Gemini extraction
/rules             Deterministic amount/date verification (Cloud Run service)
/matching          Name-matching service (Cloud Run service)
/bigquery          SQL DDL + duplicate/fraud-ring detection queries
/ml                 Risk model training notebook/scripts (BQML or AutoML)
/synthetic_data     PDF generator + fraud injection + ground-truth CSV
/report             Gemini report-writer prompt + service
/frontend           Claim upload UI
/docs               README, architecture diagram, eval results
PROJECT.md          This file
```

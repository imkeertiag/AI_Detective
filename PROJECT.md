# AI Detective project brief

This workspace is the local MVP for AI Detective, a document-risk and fraud-detection platform.

The product is intended for organizations that receive many claims or contract-related submissions per day and need a fast first-pass screening layer before human review.

Business problem:
- insurance claims need review for amount, identity, and policy-validity mismatches
- contract and legal documents may contain one-sided or unfair clauses
- document fraud can lead to money loss or regulatory exposure

Technical direction:
- Python FastAPI backend
- React.js frontend
- Google Cloud deployment architecture
- deterministic fraud checks and explainable signals
- optional AI document extraction/reporting from OpenRouter/Gemini/Ollama

Core implementation notes:
- amount inflation is calculated with deterministic code
- name matching uses phonetic and fuzzy similarity logic
- duplicate detection checks historical records
- the local frontend and backend are connected for a working demo

For the original business spec, see `fraud-analyzer-project-spec.md`.

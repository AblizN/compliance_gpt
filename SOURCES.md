# Sources

This document records the provenance of every regulatory text used by ComplianceGPT. Each entry identifies the exact version of the source document so that ingestion, embeddings, and answers can be traced back to a specific, verifiable text.

## Regulatory Documents

| Regulation         | Official URL                                  | Version              | Downloaded | File                |
|--------------------|-----------------------------------------------|----------------------|------------|---------------------|
| GDPR (EU) 2016/679 | https://eur-lex.europa.eu/eli/reg/2016/679/oj | OJ L 119, 2016-05-04 | 2026-10-05 | `data/raw/gdpr.pdf` |

## Conventions

- All dates use ISO 8601 format (`YYYY-MM-DD`).
- Only official publishers are used as sources (e.g., EUR-Lex for EU legislation).
- When a source is updated, the existing row is revised and the new version is re-ingested.

## Storage Decision

Source PDFs are committed to git under `data/raw/`, not downloaded by script.

- **Reproducibility:** the ingested file is pinned to a commit.
- **Size:** files are small (GDPR PDF is under 1 MB).
- **Simplicity:** no download step needed to re-run ingestion.

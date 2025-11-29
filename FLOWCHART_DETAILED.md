# Flowchart — Detailed Technical Walkthrough

This document expands the color-coded flowchart into a step-by-step explanation intended for technical reviewers.

## High-level goals
- Provide a robust, auditable pipeline to extract small sample data from PostgreSQL tables.
- Convert rows into compact textual representations suitable for LLM input.
- Protect against token overflow by truncating or chunking inputs before sending to the model.
- Produce both a concise summary and targeted follow-up questions to guide analysis.

## Steps (numbered to match flowchart)

1. **Start**
   - Pipeline initialization and configuration loading (environment variables).

2. **Fetch data from PostgreSQL DB**
   - Use connection pooling or context managers to open connections securely.
   - Limit results (e.g., `LIMIT 5`) to keep sample sizes small for previews.

3. **Rows returned? (Decision)**
   - If rows are returned, proceed to formatting stage.
   - If not, write a small placeholder note (`No data available from <label>`).

4. **Format rows into text**
   - Convert each row to a concise CSV-like string, escaping problematic characters.
   - Example: `id, date, customer_id, amount, comment` -> `1, 2024-01-01, C123, 199.99, "First order"`

5. **Add table text to combined_text**
   - Append per-table snippets to a single `combined_text` buffer.
   - Apply length checks and truncate aggressively if the combined payload exceeds safe thresholds.

6. **Send combined_text to LLM for Summary**
   - Use a short `system` message if available, and limit `max_tokens` for a concise output.
   - Recommended configuration: `temperature=0.2, max_tokens=200` for deterministic summaries.

7. **Receive Summary**
   - Verify response integrity and trim whitespace. Fallback gracefully if the model fails.

8. **Send Summary to LLM for Follow-up Questions**
   - Ask the model to produce exactly three follow-up questions to explore anomalies or areas of interest.

9. **Receive Follow-up Questions**
   - Verify and present questions to the user. Add safeguards for hallucination and disallowed content.

10. **End**
   - Return results to calling application or UI; log anonymized telemetry if enabled.

## Operational notes
- **Secrets management**: Never commit credentials. Use environment variables or a secrets manager.
- **Token management**: Implement chunk-and-summarize for large tables, or pre-summarize tables individually.
- **Logging**: Use structured logs (JSON) and avoid printing API keys or raw responses.
- **Retries**: Use exponential backoff for transient DB or network errors.

## Artifacts
- `flowchart_colored.mmd` — Mermaid source to regenerate the visual diagram.
- `docs/flowchart_colored.png` — Rendered PNG for documentation and README embedding.

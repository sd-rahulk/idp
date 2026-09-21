# IDP implementation review demo

1. Start Supabase-backed Next.js and the FastAPI worker.
2. Open `/signup`, create an account, confirm the email, then sign in.
3. Create a project named `AegisFlow fixture review` with no live website URL.
4. ZIP `fixtures/intentional-vulnerable-app` and upload it as the private source artifact.
5. Start the assessment. The server creates a scan row and calls the separate worker.
6. Open the scan detail page. Show the persisted task ledger and React Flow graph changing as the worker runs.
7. Show the Source Agent findings: `AF-SECRET-001`, `AF-EXEC-001`, `AF-TLS-001`, and `AF-SQL-001`. Point out that the credential excerpt is redacted.
8. Wait for validation/report completion, then open the report and use Print / export.
9. Explain that live website checks are intentionally unavailable until a target passes the well-known token verification flow. No external website is scanned in the fixture walkthrough.

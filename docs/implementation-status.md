# Implementation status

Updated: 2026-09-21

## Implemented

- Next.js App Router monorepo with strict TypeScript, Tailwind, Lucide, Framer Motion-ready design system, responsive app shell, dark operations-console visual language.
- Supabase SSR authentication surfaces: signup, login, password reset, callback, middleware route protection, server-side `getUser` checks.
- Supabase migration with ownership foreign keys, indexes, RLS policies, private source-artifact bucket, and agent-definition seed records.
- Project creation, target registration, explicit authorization confirmation, private ZIP upload, strict file-size/type validation.
- FastAPI worker with strict Pydantic contracts, safe ZIP traversal/extraction checks, separate agent modules and registry.
- Deterministic Source Security Agent with real JavaScript/TypeScript/Python checks for credential patterns, dynamic execution, disabled TLS verification, and unsafe SQL construction; secrets are redacted.
- Persisted scan/task/execution/finding/report/audit state; bounded source scope and no uploaded-code execution.
- Validator deduplication and report generation from persisted findings, including printable HTML export.
- Assessment detail with polling-based live state, React Flow workflow graph, task ledger, findings panel, cancellation endpoint.
- Dashboard metrics, project list/detail, agents, activity, settings, reports, fixture, README and security documentation.

## Partially implemented

- Worker currently dispatches source analysis and records validator/report transitions in one bounded run. A full database-backed polling queue, abandoned-job recovery, and coordinator concurrency loop are scaffolded by the schema but need the next implementation pass.
- Semgrep dependency is documented and included in the worker environment, but the deterministic fallback remains the default engine in this milestone.
- Target verification endpoint implements well-known token verification with basic DNS/private-address and redirect protections. The UI needs a dedicated challenge display/retry flow.
- Web Security Agent interface and planning slots are defined conceptually, but the runnable worker milestone focuses on source-only review.
- PDF export is print-to-PDF through a server-rendered HTML document; a containerized headless renderer is not bundled.

## Planned

- Full web agent checks for verified targets: TLS metadata, security headers, redirect chain, cookie attributes, mixed-content observations, and bounded egress.
- Transactional task claiming with `FOR UPDATE SKIP LOCKED`, bounded retries, heartbeat/abandoned-job recovery, quotas, and safe-boundary cancellation.
- Signed source repository ingestion for public GitHub URLs.
- Realtime event delivery, richer node detail drawer, finding filters, and generated PDF attachment storage.
- Expanded tests against a disposable Supabase project and an explicitly authorized local web fixture.

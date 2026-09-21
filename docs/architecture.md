# AegisFlow architecture

```mermaid
flowchart LR
  U[Authenticated user] --> W[Next.js App Router]
  W --> A[Supabase Auth]
  W --> DB[(Supabase PostgreSQL + RLS)]
  W --> ST[(Private Storage bucket)]
  W -->|worker secret| API[FastAPI worker]
  API --> DB
  API --> ST
  API --> P[Planner]
  P --> C[Coordinator]
  C --> S[Source Security Agent]
  C --> V[Validator]
  V --> R[Report Agent]
  R --> DB
```

The web server handles user/session boundaries and never sends privileged credentials to the browser. The worker owns source extraction, analysis, and report persistence. All user-facing data is read back through ownership-filtered Supabase queries.

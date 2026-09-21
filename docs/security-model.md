# Security model

## Authorization

Every project belongs to an authenticated Supabase user. RLS policies gate projects, targets, artifacts, scans, tasks, executions, findings, reports, and audit events through the owning project. API handlers also call `auth.getUser()` and query by the requested ID; changing an ID in a URL does not bypass the database policy.

## Source handling

Uploads are ZIP-only and size-limited. The worker rejects absolute paths, `..` traversal, symlinks, excessive file count, and excessive uncompressed size. Only supported text extensions are extracted for analysis. Uploaded code is read as text and never imported, executed, installed, or given shell access. Credential evidence is replaced with `[REDACTED]`.

## Live targets

Live checks require explicit authorization and a verified target. The verification endpoint uses a token served from `/.well-known/aegisflow-verification.txt`, refuses redirects, applies timeouts, and rejects local/private/link-local destinations. A production deployment must add network-level egress restrictions, revalidate every redirect hop, enforce quotas, and isolate the worker runtime.

## Evidence semantics

The source agent emits potential vulnerability findings for pattern matches and verified observations only for direct configuration signals such as disabled TLS verification. The report explicitly states that no exploitation was attempted. A missing header is not presented as a confirmed vulnerability in this milestone.

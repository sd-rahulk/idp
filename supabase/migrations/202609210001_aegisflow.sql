create extension if not exists pgcrypto;

create type public.scan_status as enum ('queued','planning','running','validating','reporting','completed','partially_completed','failed','cancelled');
create type public.task_status as enum ('pending','running','completed','failed','skipped','cancelled');
create type public.finding_severity as enum ('critical','high','medium','low','informational');
create type public.finding_kind as enum ('verified_observation','potential_vulnerability','informational','not_performed');

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 2 and 120),
  description text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.targets (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null unique references public.projects(id) on delete cascade,
  url text not null,
  hostname text not null,
  authorization_confirmed boolean not null default false,
  verification_token text,
  verified_at timestamptz,
  verification_method text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.source_artifacts (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  storage_path text not null,
  original_filename text not null,
  byte_size bigint not null,
  file_count integer not null default 0,
  content_sha256 text,
  created_at timestamptz not null default now()
);
create table public.scans (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  initiated_by uuid not null references auth.users(id) on delete restrict,
  status public.scan_status not null default 'queued',
  scope jsonb not null default '{"source": true, "web": false}'::jsonb,
  plan jsonb,
  error text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.agent_definitions (
  id text primary key,
  name text not null,
  description text not null,
  capabilities jsonb not null default '[]'::jsonb,
  enabled boolean not null default true,
  created_at timestamptz not null default now()
);
create table public.scan_tasks (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid not null references public.scans(id) on delete cascade,
  agent_id text not null references public.agent_definitions(id),
  status public.task_status not null default 'pending',
  dependencies uuid[] not null default '{}',
  input jsonb not null default '{}'::jsonb,
  output jsonb,
  attempts integer not null default 0,
  claimed_at timestamptz,
  started_at timestamptz,
  completed_at timestamptz,
  error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.agent_executions (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid not null references public.scans(id) on delete cascade,
  task_id uuid not null references public.scan_tasks(id) on delete cascade,
  agent_id text not null references public.agent_definitions(id),
  status public.task_status not null,
  input jsonb not null default '{}'::jsonb,
  output jsonb,
  logs jsonb not null default '[]'::jsonb,
  duration_ms integer,
  error text,
  created_at timestamptz not null default now()
);
create table public.findings (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid not null references public.scans(id) on delete cascade,
  task_id uuid references public.scan_tasks(id) on delete set null,
  agent_id text not null references public.agent_definitions(id),
  title text not null,
  description text not null,
  severity public.finding_severity not null,
  kind public.finding_kind not null,
  confidence text not null,
  rule_id text not null,
  asset text,
  file_path text,
  line_number integer,
  evidence jsonb not null default '{}'::jsonb,
  remediation text not null,
  duplicate_of uuid references public.findings(id) on delete set null,
  created_at timestamptz not null default now()
);
create table public.reports (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid not null unique references public.scans(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  title text not null,
  summary text not null,
  content jsonb not null,
  created_at timestamptz not null default now()
);
create table public.audit_events (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references public.projects(id) on delete cascade,
  scan_id uuid references public.scans(id) on delete cascade,
  actor_id uuid references auth.users(id) on delete set null,
  event_type text not null,
  message text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

insert into storage.buckets (id, name, public) values ('source-artifacts', 'source-artifacts', false) on conflict (id) do nothing;
create policy source_artifacts_owner_read on storage.objects for select to authenticated using (bucket_id = 'source-artifacts' and (storage.foldername(name))[1] = auth.uid()::text);
create policy source_artifacts_owner_insert on storage.objects for insert to authenticated with check (bucket_id = 'source-artifacts' and (storage.foldername(name))[1] = auth.uid()::text);
create policy source_artifacts_owner_delete on storage.objects for delete to authenticated using (bucket_id = 'source-artifacts' and (storage.foldername(name))[1] = auth.uid()::text);

create index projects_owner_created_idx on public.projects(owner_id, created_at desc);
create index scans_project_created_idx on public.scans(project_id, created_at desc);
create index scan_tasks_scan_status_idx on public.scan_tasks(scan_id, status);
create index findings_scan_severity_idx on public.findings(scan_id, severity);
create index audit_events_scan_created_idx on public.audit_events(scan_id, created_at desc);

create or replace function public.is_project_owner(project_uuid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.projects where id = project_uuid and owner_id = auth.uid());
$$;

alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.targets enable row level security;
alter table public.source_artifacts enable row level security;
alter table public.scans enable row level security;
alter table public.agent_definitions enable row level security;
alter table public.scan_tasks enable row level security;
alter table public.agent_executions enable row level security;
alter table public.findings enable row level security;
alter table public.reports enable row level security;
alter table public.audit_events enable row level security;

create policy profiles_self on public.profiles for all using (id = auth.uid()) with check (id = auth.uid());
create policy projects_owner on public.projects for all using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy targets_owner on public.targets for all using (public.is_project_owner(project_id)) with check (public.is_project_owner(project_id));
create policy artifacts_owner on public.source_artifacts for all using (public.is_project_owner(project_id)) with check (public.is_project_owner(project_id));
create policy scans_owner on public.scans for all using (public.is_project_owner(project_id)) with check (public.is_project_owner(project_id));
create policy agents_read on public.agent_definitions for select using (true);
create policy tasks_owner on public.scan_tasks for select using (exists (select 1 from public.scans s where s.id = scan_id and public.is_project_owner(s.project_id)));
create policy executions_owner on public.agent_executions for select using (exists (select 1 from public.scans s where s.id = scan_id and public.is_project_owner(s.project_id)));
create policy findings_owner on public.findings for select using (exists (select 1 from public.scans s where s.id = scan_id and public.is_project_owner(s.project_id)));
create policy reports_owner on public.reports for select using (public.is_project_owner(project_id));
create policy audit_owner on public.audit_events for select using (project_id is null or public.is_project_owner(project_id));

insert into public.agent_definitions (id, name, description, capabilities) values
('planner', 'Planner Agent', 'Builds a deterministic assessment plan from verified scope.', '["scope-analysis","task-planning"]'),
('coordinator', 'Coordinator Agent', 'Dispatches dependency-aware tasks and records execution state.', '["orchestration","retry-recovery"]'),
('web-security', 'Web Security Agent', 'Performs non-destructive checks against verified origins.', '["headers","tls","cookies","redirects"]'),
('source-security', 'Source Security Agent', 'Runs Semgrep or deterministic fallback rules against source artifacts.', '["secrets","injection","process","tls"]'),
('validator', 'Validator Agent', 'Normalizes schema, deduplicates findings, and records limitations.', '["validation","deduplication"]'),
('report', 'Report Agent', 'Builds a persisted, printable report from validated findings.', '["reporting","remediation"]')
on conflict (id) do update set name = excluded.name, description = excluded.description, capabilities = excluded.capabilities;

create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name) values (new.id, coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1)));
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute procedure public.handle_new_user();

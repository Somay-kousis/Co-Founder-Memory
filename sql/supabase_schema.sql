create extension if not exists vector;

create table if not exists public.state_store (
  id text primary key,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.memory_store (
  namespace text[] not null,
  key text not null,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (namespace, key)
);

create table if not exists public.documents (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(384)
);

create index if not exists documents_embedding_idx
on public.documents using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists state_store_touch_updated_at on public.state_store;
create trigger state_store_touch_updated_at
before update on public.state_store
for each row execute function public.touch_updated_at();

drop trigger if exists memory_store_touch_updated_at on public.memory_store;
create trigger memory_store_touch_updated_at
before update on public.memory_store
for each row execute function public.touch_updated_at();

create or replace function public.match_documents(
  query_embedding vector(384),
  match_count int default 5,
  filter jsonb default '{}'::jsonb
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from public.documents
  where filter = '{}'::jsonb or documents.metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

alter table public.state_store disable row level security;
alter table public.memory_store disable row level security;
alter table public.documents disable row level security;

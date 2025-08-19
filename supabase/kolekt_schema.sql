-- Kolekt initial schema for curation, embeddings, scheduling
-- Safe to run multiple times (IF NOT EXISTS guards)

-- Enable pgvector (Supabase supports this extension)
create extension if not exists vector;

-- Sources the user connects (RSS, Notion, YouTube, etc.)
create table if not exists content_sources (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  type text not null,           -- rss | webpage | notion | youtube | twitter | reddit | manual
  name text not null,
  url text,
  config jsonb default '{}'::jsonb,
  trust_score numeric default 0.7, -- 0..1 baseline quality
  is_active boolean default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Raw normalized items pulled from sources
create table if not exists content_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  source_id uuid references content_sources(id) on delete set null,
  external_id text,            -- id from the source (guid/url)
  title text,
  author text,
  url text,
  published_at timestamptz,
  lang text,
  raw text,                    -- original text (transcript, article, etc.)
  normalized text,             -- cleaned text (plain)
  metadata jsonb default '{}'::jsonb,
  added_at timestamptz default now(),
  unique(user_id, source_id, external_id)
);

-- Dense vector per content_item for semantic tasks
create table if not exists content_embeddings (
  item_id uuid primary key references content_items(id) on delete cascade,
  embedding vector(768) -- adjust if using different model size
);

-- Items awaiting human approval or auto-post processing
create table if not exists review_queue (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  item_id uuid references content_items(id) on delete cascade,
  score numeric not null default 0,
  reasons text[],
  status text not null default 'pending', -- pending | approved | rejected | drafted
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Drafts generated for channels (Threads/IG/FB)
create table if not exists channel_drafts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  item_id uuid references content_items(id) on delete set null,
  channel text not null,           -- threads | instagram | facebook
  variant int not null default 1,
  content jsonb not null,          -- structured posts array, images, hashtags
  quality jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- Schedules for posting
create table if not exists post_schedules (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  channel text not null,
  draft_id uuid references channel_drafts(id) on delete cascade,
  scheduled_for timestamptz not null,
  auto_post boolean default false,
  status text not null default 'queued', -- queued | posting | posted | failed | canceled
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Logged results from posting
create table if not exists channel_posts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  channel text not null,
  draft_id uuid references channel_drafts(id) on delete set null,
  external_post_id text,
  success boolean default false,
  error text,
  posted_at timestamptz,
  created_at timestamptz default now()
);

-- Engagement metrics
create table if not exists engagement_metrics (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  channel text not null,
  post_id uuid references channel_posts(id) on delete cascade,
  impressions int default 0,
  likes int default 0,
  comments int default 0,
  shares int default 0,
  captured_at timestamptz default now()
);



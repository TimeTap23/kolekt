-- Social Media Connections Schema
-- Stores persistent OAuth connections for social media platforms

-- Social media platform connections
create table if not exists social_connections (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  platform text not null,
  account_id text not null,
  username text not null,
  display_name text,
  profile_pic_url text,
  access_token text not null,
  refresh_token text,
  token_expires_at timestamptz,
  scopes text[] not null default '{}',
  followers_count integer default 0,
  following_count integer default 0,
  is_active boolean default true,
  last_sync_at timestamptz default now(),
  connected_at timestamptz default now(),
  updated_at timestamptz default now(),
  
  -- Ensure one connection per user per platform
  unique(user_id, platform),
  
  -- Index for quick lookups
  constraint valid_platform check (platform in ('threads', 'instagram', 'facebook'))
);

-- Index for performance
create index if not exists idx_social_connections_user_platform 
  on social_connections(user_id, platform);

create index if not exists idx_social_connections_active 
  on social_connections(user_id, is_active) where is_active = true;

-- Function to update the updated_at timestamp
create or replace function update_social_connections_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Trigger to automatically update updated_at
create trigger trigger_update_social_connections_updated_at
  before update on social_connections
  for each row
  execute function update_social_connections_updated_at();

-- Function to encrypt sensitive data (placeholder - implement proper encryption)
create or replace function encrypt_social_token(token text)
returns text as $$
begin
  -- In production, use proper encryption like pgcrypto
  -- For now, return as-is (should be encrypted in production)
  return token;
end;
$$ language plpgsql;

-- Function to decrypt sensitive data (placeholder - implement proper decryption)
create or replace function decrypt_social_token(encrypted_token text)
returns text as $$
begin
  -- In production, use proper decryption like pgcrypto
  -- For now, return as-is (should be decrypted in production)
  return encrypted_token;
end;
$$ language plpgsql;

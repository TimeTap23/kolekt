-- Social Media Connections Schema
-- Stores persistent OAuth connections for social media platforms

-- Social media platform connections
create table if not exists social_connections (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  platform text not null,                    -- threads | instagram | facebook
  account_id text not null,                  -- Platform's account ID
  username text not null,                    -- Platform username
  display_name text,                         -- Display name on platform
  profile_pic_url text,                      -- Profile picture URL
  access_token text not null,                -- OAuth access token (encrypted)
  refresh_token text,                        -- OAuth refresh token (encrypted)
  token_expires_at timestamptz,              -- When access token expires
  scopes text[] not null default '{}',       -- Granted permissions
  followers_count integer default 0,
  following_count integer default 0,
  is_active boolean default true,            -- Whether connection is active
  last_sync_at timestamptz default now(),    -- Last time we synced data
  connected_at timestamptz default now(),    -- When connection was established
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

-- Insert some sample data for testing (remove in production)
insert into social_connections (
  user_id, 
  platform, 
  account_id, 
  username, 
  display_name, 
  profile_pic_url,
  access_token,
  refresh_token,
  token_expires_at,
  scopes,
  followers_count,
  following_count
) values 
(
  '550e8400-e29b-41d4-a716-446655440000',
  'threads',
  'threads_123456',
  'kolekt_user',
  'Kolekt User',
  'https://via.placeholder.com/150x150?text=TU',
  encrypt_social_token('sample_access_token_123'),
  encrypt_social_token('sample_refresh_token_123'),
  now() + interval '60 days',
  array['read_posts', 'write_posts', 'read_profile'],
  1250,
  625
),
(
  '550e8400-e29b-41d4-a716-446655440000',
  'facebook',
  'facebook_345678',
  'kolekt.fb',
  'Kolekt Facebook',
  'https://via.placeholder.com/150x150?text=KF',
  encrypt_social_token('sample_access_token_456'),
  encrypt_social_token('sample_refresh_token_456'),
  now() + interval '60 days',
  array['read_posts', 'write_posts', 'read_profile', 'manage_pages'],
  2100,
  1050
)
on conflict (user_id, platform) do nothing;

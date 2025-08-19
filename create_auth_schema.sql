-- Create authentication schema for Kolekt

-- Create profiles table if it doesn't exist
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    plan VARCHAR(50) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);

-- Insert a test user for development
INSERT INTO profiles (id, email, name, password_hash, role, plan, is_active, is_verified, email_verified)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'test@example.com',
    'Test User',
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', -- password: 123
    'user',
    'free',
    true,
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert another test user
INSERT INTO profiles (id, email, name, password_hash, role, plan, is_active, is_verified, email_verified)
VALUES (
    '550e8400-e29b-41d4-a716-446655440001',
    'admin@example.com',
    'Admin User',
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', -- password: 123
    'admin',
    'premium',
    true,
    true,
    true
) ON CONFLICT (email) DO NOTHING;

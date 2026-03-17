-- Create tables and default admin user for Trade Finance Platform
-- This script runs on first database initialization

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    type VARCHAR(50) DEFAULT 'BRANCH',
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Branches table
CREATE TABLE IF NOT EXISTS branches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    branch_id UUID REFERENCES branches(id),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    phone VARCHAR(20),
    phone_country_code VARCHAR(10),
    organization_id UUID REFERENCES organizations(id),
    branch_id UUID REFERENCES branches(id),
    department_id UUID REFERENCES departments(id),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(100),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(50),
    password_changed_at TIMESTAMP,
    password_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User-Roles association table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by UUID,
    PRIMARY KEY (user_id, role_id)
);

-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Role-Permissions association table
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    refresh_token_hash VARCHAR(255),
    ip_address VARCHAR(50),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default organization
INSERT INTO organizations (id, name, code, type, is_active)
SELECT uuid_generate_v4(), 'Trade Finance Bank', 'TFB', 'HEADQUARTERS', true
WHERE NOT EXISTS (SELECT 1 FROM organizations WHERE code = 'TFB');

-- Insert default branch
INSERT INTO branches (id, name, code, organization_id, is_active)
SELECT 
    uuid_generate_v4(), 
    'Main Branch', 
    'MB001', 
    (SELECT id FROM organizations WHERE code = 'TFB'),
    true
WHERE NOT EXISTS (SELECT 1 FROM branches WHERE code = 'MB001');

-- Insert default department
INSERT INTO departments (id, name, code, branch_id, is_active)
SELECT 
    uuid_generate_v4(), 
    'Trade Finance Department', 
    'TFD001', 
    (SELECT id FROM branches WHERE code = 'MB001'),
    true
WHERE NOT EXISTS (SELECT 1 FROM departments WHERE code = 'TFD001');

-- Insert default roles
INSERT INTO roles (id, name, description) VALUES
    (uuid_generate_v4(), 'ADMIN', 'System Administrator with full access'),
    (uuid_generate_v4(), 'RELATIONSHIP_MANAGER', 'Manages customer relationships and trade transactions'),
    (uuid_generate_v4(), 'CREDIT_OFFICER', 'Evaluates credit applications and risk'),
    (uuid_generate_v4(), 'OPERATIONS', 'Handles document processing and operational tasks'),
    (uuid_generate_v4(), 'COMPLIANCE', 'Manages compliance and KYC verification'),
    (uuid_generate_v4(), 'VIEWER', 'Read-only access to view transactions')
ON CONFLICT (name) DO NOTHING;

-- Insert admin user (password: admin123 - hashed with bcrypt)
-- The password hash corresponds to 'admin123'
INSERT INTO users (
    id,
    email,
    username,
    password_hash,
    first_name,
    last_name,
    branch_id,
    department_id,
    status,
    is_active,
    is_verified,
    is_mfa_enabled,
    created_at,
    updated_at
) SELECT 
    uuid_generate_v4(),
    'admin@tradefinance.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS.xJ5m3S',
    'System',
    'Administrator',
    (SELECT id FROM branches WHERE code = 'MB001'),
    (SELECT id FROM departments WHERE code = 'TFD001'),
    'ACTIVE',
    true,
    true,
    false,
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- Assign admin role to admin user
INSERT INTO user_roles (user_id, role_id)
SELECT 
    u.id, 
    r.id
FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'ADMIN'
ON CONFLICT DO NOTHING;

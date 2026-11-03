-- ============================================================================
-- Financial Fraud Detection & Risk Scoring API
-- Relational Database Schema (SQLite / PostgreSQL Compatible)
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    home_country VARCHAR(3) NOT NULL DEFAULT 'USA',
    home_lat REAL NOT NULL,
    home_lon REAL NOT NULL,
    risk_segment VARCHAR(20) DEFAULT 'STANDARD',
    account_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    device_fingerprint VARCHAR(64) NOT NULL,
    device_type VARCHAR(20) NOT NULL, -- 'MOBILE', 'DESKTOP', 'TABLET'
    operating_system VARCHAR(50),
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_trusted BOOLEAN DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS merchants (
    merchant_id VARCHAR(36) PRIMARY KEY,
    merchant_name VARCHAR(100) NOT NULL,
    merchant_category VARCHAR(50) NOT NULL, -- 'grocery', 'electronics', 'crypto', 'luxury', 'travel', etc.
    risk_level VARCHAR(20) DEFAULT 'LOW', -- 'LOW', 'MEDIUM', 'HIGH'
    country VARCHAR(3) DEFAULT 'USA'
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    merchant_id VARCHAR(36) NOT NULL,
    device_id VARCHAR(36),
    amount REAL NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    channel VARCHAR(20) NOT NULL, -- 'WEB', 'MOBILE_APP', 'POS_CHIP', 'POS_SWIPE', 'ATM', 'API'
    status VARCHAR(20) DEFAULT 'COMPLETED',
    timestamp TIMESTAMP NOT NULL,
    epoch_timestamp INTEGER NOT NULL,
    ip_address VARCHAR(45),
    geo_lat REAL,
    geo_lon REAL,
    is_foreign_transaction INTEGER DEFAULT 0,
    failed_pin_attempts INTEGER DEFAULT 0,
    is_fraud INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(merchant_id) REFERENCES merchants(merchant_id),
    FOREIGN KEY(device_id) REFERENCES devices(device_id)
);

CREATE INDEX IF NOT EXISTS idx_trans_user_time ON transactions(user_id, epoch_timestamp);
CREATE INDEX IF NOT EXISTS idx_trans_fraud ON transactions(is_fraud);
CREATE INDEX IF NOT EXISTS idx_trans_merchant ON transactions(merchant_id);

-- ============================================================================
-- Complex Analytical & Feature Engineering SQL Queries
-- Rolling Window Functions, Behavioral Aggregations, & Risk Heuristics
-- ============================================================================

-- Query 1: Automated Feature Extraction with 1-Hour & 24-Hour Rolling Windows
-- Computes rolling transaction frequency, ratio to 30-day customer baseline, and device novelty
WITH UserHistoricalBaselines AS (
    SELECT 
        user_id,
        AVG(amount) AS avg_historical_amount_30d,
        COUNT(*) AS total_transactions_30d,
        MAX(epoch_timestamp) AS last_seen_epoch
    FROM transactions
    WHERE epoch_timestamp >= (strftime('%s', 'now') - 2592000)
    GROUP BY user_id
),
RecentVelocity AS (
    SELECT 
        t.transaction_id,
        t.user_id,
        t.amount,
        t.merchant_id,
        t.channel,
        t.timestamp,
        t.epoch_timestamp,
        t.geo_lat,
        t.geo_lon,
        t.failed_pin_attempts,
        t.is_foreign_transaction,
        t.is_fraud,
        -- Rolling 1-Hour (3600 seconds) Transaction Velocity
        COUNT(*) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.epoch_timestamp 
            RANGE BETWEEN 3600 PRECEDING AND CURRENT ROW
        ) - 1 AS velocity_1h,
        -- Rolling 24-Hour (86400 seconds) Transaction Velocity
        COUNT(*) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.epoch_timestamp 
            RANGE BETWEEN 86400 PRECEDING AND CURRENT ROW
        ) - 1 AS velocity_24h,
        -- Rolling 24-Hour Cumulative Spend
        SUM(t.amount) OVER (
            PARTITION BY t.user_id 
            ORDER BY t.epoch_timestamp 
            RANGE BETWEEN 86400 PRECEDING AND CURRENT ROW
        ) AS cumulative_spend_24h,
        -- Lagged coordinates for travel velocity calculations
        LAG(t.geo_lat, 1) OVER (PARTITION BY t.user_id ORDER BY t.epoch_timestamp) AS prev_lat,
        LAG(t.geo_lon, 1) OVER (PARTITION BY t.user_id ORDER BY t.epoch_timestamp) AS prev_lon,
        LAG(t.epoch_timestamp, 1) OVER (PARTITION BY t.user_id ORDER BY t.epoch_timestamp) AS prev_epoch
    FROM transactions t
)
SELECT 
    v.transaction_id,
    v.user_id,
    v.amount,
    v.velocity_1h,
    v.velocity_24h,
    v.cumulative_spend_24h,
    v.channel,
    m.merchant_category,
    m.risk_level AS merchant_risk_level,
    ROUND(v.amount / NULLIF(b.avg_historical_amount_30d, 0), 2) AS amount_to_avg_ratio_30d,
    CASE 
        WHEN d.device_id IS NULL THEN 1 
        WHEN d.is_trusted = 0 THEN 1 
        ELSE 0 
    END AS is_new_device,
    -- Haversine approximate distance from user's registered home coordinates (km)
    ROUND(
        6371 * 2 * ASIN(
            SQRT(
                POWER(SIN(RADIANS(v.geo_lat - u.home_lat) / 2), 2) +
                COS(RADIANS(u.home_lat)) * COS(RADIANS(v.geo_lat)) *
                POWER(SIN(RADIANS(v.geo_lon - u.home_lon) / 2), 2)
            )
        ), 2
    ) AS distance_from_home_km,
    v.is_foreign_transaction,
    v.failed_pin_attempts,
    v.is_fraud
FROM RecentVelocity v
JOIN users u ON v.user_id = u.user_id
JOIN merchants m ON v.merchant_id = m.merchant_id
LEFT JOIN devices d ON v.user_id = d.user_id AND d.is_trusted = 1
LEFT JOIN UserHistoricalBaselines b ON v.user_id = b.user_id;


-- Query 2: High-Risk Category & Hourly Behavioral Anomaly Aggregation
SELECT 
    m.merchant_category,
    COUNT(t.transaction_id) AS total_tx_count,
    ROUND(SUM(t.amount), 2) AS total_volume,
    SUM(t.is_fraud) AS fraudulent_tx_count,
    ROUND(100.0 * SUM(t.is_fraud) / COUNT(t.transaction_id), 2) AS fraud_rate_percentage,
    ROUND(AVG(t.amount), 2) AS average_amount,
    ROUND(MAX(t.amount), 2) AS max_amount
FROM transactions t
JOIN merchants m ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_category
ORDER BY fraud_rate_percentage DESC;


-- Query 3: Impossible Travel Speed Anomaly Detector
-- Flags consecutive transactions separated by distances that require supersonic travel (> 800 km/h)
WITH LaggedTransactions AS (
    SELECT 
        transaction_id,
        user_id,
        amount,
        epoch_timestamp,
        geo_lat,
        geo_lon,
        LAG(geo_lat, 1) OVER (PARTITION BY user_id ORDER BY epoch_timestamp) AS prev_lat,
        LAG(geo_lon, 1) OVER (PARTITION BY user_id ORDER BY epoch_timestamp) AS prev_lon,
        LAG(epoch_timestamp, 1) OVER (PARTITION BY user_id ORDER BY epoch_timestamp) AS prev_epoch
    FROM transactions
)
SELECT 
    transaction_id,
    user_id,
    amount,
    (epoch_timestamp - prev_epoch) / 3600.0 AS time_delta_hours,
    ROUND(
        6371 * 2 * ASIN(
            SQRT(
                POWER(SIN(RADIANS(geo_lat - prev_lat) / 2), 2) +
                COS(RADIANS(prev_lat)) * COS(RADIANS(geo_lat)) *
                POWER(SIN(RADIANS(geo_lon - prev_lon) / 2), 2)
            )
        ), 2
    ) AS distance_traveled_km,
    ROUND(
        (6371 * 2 * ASIN(
            SQRT(
                POWER(SIN(RADIANS(geo_lat - prev_lat) / 2), 2) +
                COS(RADIANS(prev_lat)) * COS(RADIANS(geo_lat)) *
                POWER(SIN(RADIANS(geo_lon - prev_lon) / 2), 2)
            )
        )) / NULLIF(((epoch_timestamp - prev_epoch) / 3600.0), 0), 2
    ) AS implied_speed_kmh
FROM LaggedTransactions
WHERE prev_epoch IS NOT NULL 
  AND (epoch_timestamp - prev_epoch) > 0
  AND (epoch_timestamp - prev_epoch) < 14400 -- within 4 hours
HAVING implied_speed_kmh > 800.0
ORDER BY implied_speed_kmh DESC;

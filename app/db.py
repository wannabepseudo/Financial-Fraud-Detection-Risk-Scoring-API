"""
Database Utilities & Analytical Query Engine
"""

import sqlite3
import os
import math
from typing import Dict, Any, List, Optional
from app.config import DB_PATH


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_profile_and_velocity(user_id: str) -> Dict[str, Any]:
    """
    Fetches customer 30-day spending baseline, coordinates, and recent velocity.
    Returns safe default values if customer is not found (cold start).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check user registration
        cursor.execute("SELECT home_lat, home_lon, risk_segment FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()

        if not user_row:
            return {
                "exists": False,
                "mean_amount": 75.0,
                "home_lat": 40.7128,
                "home_lon": -74.0060,
                "velocity_1h": 0,
                "velocity_24h": 0,
                "cumulative_spend_24h": 0.0
            }

        home_lat = user_row["home_lat"]
        home_lon = user_row["home_lon"]

        # Calculate 30-day baseline average & 24h velocity
        cursor.execute("""
            SELECT 
                AVG(amount) as avg_amt,
                COUNT(*) as count_30d
            FROM transactions
            WHERE user_id = ?
        """, (user_id,))
        stats = cursor.fetchone()
        mean_amt = stats["avg_amt"] if stats and stats["avg_amt"] else 75.0

        return {
            "exists": True,
            "mean_amount": float(mean_amt),
            "home_lat": float(home_lat),
            "home_lon": float(home_lon),
            "velocity_1h": 0,
            "velocity_24h": 1,
            "cumulative_spend_24h": float(mean_amt)
        }
    finally:
        conn.close()


def get_analytics_summary() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*), SUM(is_fraud), SUM(amount), AVG(amount) FROM transactions")
        total_tx, fraud_tx, total_vol, avg_amt = cursor.fetchone()

        # Merchant category breakdown
        cursor.execute("""
            SELECT 
                m.merchant_category,
                COUNT(t.transaction_id) as tx_count,
                SUM(t.is_fraud) as fraud_count,
                ROUND(100.0 * SUM(t.is_fraud) / COUNT(t.transaction_id), 2) as fraud_rate_pct,
                ROUND(AVG(t.amount), 2) as avg_amount
            FROM transactions t
            JOIN merchants m ON t.merchant_id = m.merchant_id
            GROUP BY m.merchant_category
            ORDER BY fraud_rate_pct DESC
        """)
        categories = [dict(row) for row in cursor.fetchall()]

        # Channel breakdown
        cursor.execute("""
            SELECT 
                channel,
                COUNT(*) as tx_count,
                SUM(is_fraud) as fraud_count,
                ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) as fraud_rate_pct
            FROM transactions
            GROUP BY channel
            ORDER BY tx_count DESC
        """)
        channels = [dict(row) for row in cursor.fetchall()]

        return {
            "total_transactions": total_tx,
            "fraud_transactions": fraud_tx or 0,
            "fraud_rate_pct": round(100.0 * (fraud_tx or 0) / (total_tx or 1), 2),
            "total_volume_usd": round(total_vol or 0.0, 2),
            "average_transaction_usd": round(avg_amt or 0.0, 2),
            "categories": categories,
            "channels": channels
        }
    finally:
        conn.close()


def get_recent_transactions(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                t.transaction_id,
                t.user_id,
                t.amount,
                t.channel,
                t.timestamp,
                t.is_foreign_transaction,
                t.failed_pin_attempts,
                t.is_fraud,
                m.merchant_name,
                m.merchant_category
            FROM transactions t
            JOIN merchants m ON t.merchant_id = m.merchant_id
            ORDER BY t.epoch_timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def execute_analytical_query(query_id: str) -> Dict[str, Any]:
    """
    Executes one of the production SQL queries defined in queries.sql
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if query_id == "merchant_risks":
            sql = """
            SELECT 
                m.merchant_category,
                COUNT(t.transaction_id) AS total_tx_count,
                ROUND(SUM(t.amount), 2) AS total_volume,
                SUM(t.is_fraud) AS fraudulent_tx_count,
                ROUND(100.0 * SUM(t.is_fraud) / COUNT(t.transaction_id), 2) AS fraud_rate_percentage,
                ROUND(AVG(t.amount), 2) AS average_amount
            FROM transactions t
            JOIN merchants m ON t.merchant_id = m.merchant_id
            GROUP BY m.merchant_category
            ORDER BY fraud_rate_percentage DESC
            LIMIT 15;
            """
        elif query_id == "impossible_travel":
            sql = """
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
                ROUND((epoch_timestamp - prev_epoch) / 3600.0, 2) AS time_delta_hours,
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
              AND (epoch_timestamp - prev_epoch) < 14400
              AND implied_speed_kmh > 800.0
            ORDER BY implied_speed_kmh DESC
            LIMIT 10;
            """
        else:  # rolling_velocities
            sql = """
            WITH RecentVelocity AS (
                SELECT 
                    t.transaction_id,
                    t.user_id,
                    t.amount,
                    t.channel,
                    t.is_fraud,
                    COUNT(*) OVER (
                        PARTITION BY t.user_id 
                        ORDER BY t.epoch_timestamp 
                        RANGE BETWEEN 3600 PRECEDING AND CURRENT ROW
                    ) - 1 AS velocity_1h,
                    COUNT(*) OVER (
                        PARTITION BY t.user_id 
                        ORDER BY t.epoch_timestamp 
                        RANGE BETWEEN 86400 PRECEDING AND CURRENT ROW
                    ) - 1 AS velocity_24h,
                    ROUND(SUM(t.amount) OVER (
                        PARTITION BY t.user_id 
                        ORDER BY t.epoch_timestamp 
                        RANGE BETWEEN 86400 PRECEDING AND CURRENT ROW
                    ), 2) AS cumulative_spend_24h
                FROM transactions t
            )
            SELECT * FROM RecentVelocity 
            WHERE velocity_1h >= 2
            ORDER BY velocity_1h DESC 
            LIMIT 15;
            """

        cursor.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
        columns = list(rows[0].keys()) if rows else []

        return {
            "query_id": query_id,
            "sql": sql.strip(),
            "columns": columns,
            "row_count": len(rows),
            "rows": rows
        }
    finally:
        conn.close()

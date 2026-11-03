"""
Exploratory Data Analysis (EDA) & Behavioral Analytics
Generates publication-quality visualizations with Matplotlib & Seaborn:
- Class Imbalance & Transaction Volume
- Transaction Amount Distributions (Log-Scale)
- Feature Correlation Matrix
- Hourly Fraud Rate Behavioral Anomaly Curve
- Model ROC & Precision-Recall Curves
- Top Anomaly Driver Importances
"""

import os
import sqlite3
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "transactions.db")
EDA_DIR = os.path.join(BASE_DIR, "eda", "plots")
STATIC_EDA_DIR = os.path.join(BASE_DIR, "static", "eda")
METRICS_PATH = os.path.join(BASE_DIR, "models", "model_artifacts", "metrics.json")

os.makedirs(EDA_DIR, exist_ok=True)
os.makedirs(STATIC_EDA_DIR, exist_ok=True)

# Styling
plt.style.use('dark_background')
plt.rcParams['font.sans-serif'] = 'Segoe UI, Helvetica, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#1e293b'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

COLOR_LEGIT = '#10b981'   # Emerald Green
COLOR_FRAUD = '#ef4444'   # Crimson Red
COLOR_PRIMARY = '#6366f1' # Indigo
COLOR_ACCENT = '#38bdf8'  # Cyan


def save_plot(fig, filename):
    p1 = os.path.join(EDA_DIR, filename)
    p2 = os.path.join(STATIC_EDA_DIR, filename)
    fig.savefig(p1, dpi=200, bbox_inches='tight', facecolor='#0b0f19')
    fig.savefig(p2, dpi=200, bbox_inches='tight', facecolor='#0b0f19')
    plt.close(fig)
    print(f"[+] Saved {filename}")


def run_eda():
    print("[*] Loading database records for EDA...")
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        t.transaction_id,
        t.user_id,
        t.amount,
        t.channel,
        t.timestamp,
        t.epoch_timestamp,
        t.geo_lat,
        t.geo_lon,
        t.is_foreign_transaction,
        t.failed_pin_attempts,
        t.is_fraud,
        u.home_lat,
        u.home_lon,
        m.merchant_category,
        m.risk_level AS merchant_risk
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    JOIN merchants m ON t.merchant_id = m.merchant_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['dt'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    df['hour'] = df['dt'].dt.hour
    
    # Haversine distance
    lat1 = np.radians(df['home_lat'])
    lat2 = np.radians(df['geo_lat'])
    dlat = np.radians(df['geo_lat'] - df['home_lat'])
    dlon = np.radians(df['geo_lon'] - df['home_lon'])
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    df['distance_from_home_km'] = np.round(6371.0 * c, 2)

    # 1. Class Distribution Plot
    print("[*] Generating Class Imbalance plot...")
    fig, ax = plt.subplots(figsize=(8, 5))
    counts = df['is_fraud'].value_counts()
    labels = ['Legitimate (0)', 'Fraudulent (1)']
    colors = [COLOR_LEGIT, COLOR_FRAUD]
    bars = ax.bar(labels, counts.values, color=colors, width=0.45, edgecolor='#475569', linewidth=1.2)
    
    for bar in bars:
        yval = bar.get_height()
        pct = (yval / len(df)) * 100
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 500, f"{yval:,} ({pct:.1f}%)",
                ha='center', va='bottom', color='#f8fafc', fontweight='bold', fontsize=11)
    
    ax.set_title("Financial Transaction Class Imbalance Distribution", fontsize=14, fontweight='bold', pad=15, color='#f8fafc')
    ax.set_ylabel("Transaction Count", fontsize=11, color='#94a3b8')
    ax.grid(axis='y')
    ax.set_ylim(0, len(df) * 1.05)
    save_plot(fig, "class_imbalance.png")

    # 2. Transaction Amount Distribution (Log-Scale)
    print("[*] Generating Amount Distribution (Log-Scale)...")
    fig, ax = plt.subplots(figsize=(9, 5))
    legit_amt = df[df['is_fraud'] == 0]['amount']
    fraud_amt = df[df['is_fraud'] == 1]['amount']

    bins = np.logspace(np.log10(max(1, df['amount'].min())), np.log10(df['amount'].max()), 50)
    ax.hist(legit_amt, bins=bins, alpha=0.65, color=COLOR_LEGIT, label=f'Legitimate (Median: ${legit_amt.median():.1f})', density=True)
    ax.hist(fraud_amt, bins=bins, alpha=0.75, color=COLOR_FRAUD, label=f'Fraudulent (Median: ${fraud_amt.median():.1f})', density=True)

    ax.set_xscale('log')
    ax.set_title("Transaction Amount Distribution: Legitimate vs Fraud (Log-Scale)", fontsize=14, fontweight='bold', pad=15, color='#f8fafc')
    ax.set_xlabel("Transaction Amount in USD (Log Scale)", fontsize=11, color='#94a3b8')
    ax.set_ylabel("Probability Density", fontsize=11, color='#94a3b8')
    ax.legend(frameon=True, facecolor='#1e293b', edgecolor='#334155', fontsize=10)
    ax.grid(True)
    save_plot(fig, "amount_distribution_log.png")

    # 3. Correlation Matrix Heatmap
    print("[*] Generating Feature Correlation Matrix...")
    fig, ax = plt.subplots(figsize=(8.5, 7))
    corr_cols = ['amount', 'distance_from_home_km', 'is_foreign_transaction', 'failed_pin_attempts', 'hour', 'is_fraud']
    corr_labels = ['Amount ($)', 'Distance Home (km)', 'Foreign Country', 'Failed PINs', 'Hour of Day', 'Fraud Label']
    
    sub_df = df[corr_cols].copy()
    sub_df.columns = corr_labels
    corr = sub_df.corr()

    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', vmin=-0.2, vmax=0.6,
                linewidths=1, linecolor='#0f172a', ax=ax, cbar_kws={'label': 'Correlation Coefficient'})
    
    ax.set_title("Behavioral Anomaly & Risk Factor Correlation Matrix", fontsize=14, fontweight='bold', pad=15, color='#f8fafc')
    plt.xticks(rotation=30, ha='right', color='#e2e8f0')
    plt.yticks(rotation=0, color='#e2e8f0')
    save_plot(fig, "correlation_matrix.png")

    # 4. Hourly Anomaly Curve
    print("[*] Generating Hourly Fraud Rate Curve...")
    fig, ax1 = plt.subplots(figsize=(10, 5))
    hourly = df.groupby('hour').agg(
        total_tx=('transaction_id', 'count'),
        fraud_tx=('is_fraud', 'sum')
    ).reset_index()
    hourly['fraud_rate'] = (hourly['fraud_tx'] / hourly['total_tx']) * 100

    ax2 = ax1.twinx()
    ax1.bar(hourly['hour'], hourly['total_tx'], color='#334155', alpha=0.5, label='Total Volume (Count)')
    ax2.plot(hourly['hour'], hourly['fraud_rate'], color='#f59e0b', marker='o', linewidth=2.5, label='Fraud Attack Rate (%)')
    ax2.scatter(hourly.loc[hourly['fraud_rate'].idxmax()]['hour'], hourly['fraud_rate'].max(),
                color=COLOR_FRAUD, s=120, zorder=5, label='Peak Anomaly Hour')

    ax1.set_xlabel("Hour of Day (UTC 00:00 - 23:00)", fontsize=11, color='#94a3b8')
    ax1.set_ylabel("Total Transaction Volume", fontsize=11, color='#94a3b8')
    ax2.set_ylabel("Fraud Attack Rate (%)", fontsize=11, color='#f59e0b')
    ax1.set_xticks(range(0, 24, 2))
    ax1.set_title("Temporal Anomaly Analysis: High-Risk Off-Hours Surge", fontsize=14, fontweight='bold', pad=15, color='#f8fafc')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', facecolor='#1e293b', edgecolor='#334155')
    save_plot(fig, "hourly_anomaly_curve.png")

    # 5. ROC Curve & PR Curve from metrics if available
    if os.path.exists(METRICS_PATH):
        print("[*] Generating ROC and PR Curves from model metrics...")
        with open(METRICS_PATH, 'r') as f:
            m_data = json.load(f)
        
        roc_pts = m_data.get('curves', {}).get('roc', [])
        pr_pts = m_data.get('curves', {}).get('pr', [])
        auc_val = m_data.get('metrics', {}).get('auc_roc', 0.94)
        prec_val = m_data.get('metrics', {}).get('precision', 0.88)

        if roc_pts and pr_pts:
            fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(14, 5.5))

            # ROC
            fprs = [p['fpr'] for p in roc_pts]
            tprs = [p['tpr'] for p in roc_pts]
            ax_roc.plot(fprs, tprs, color=COLOR_PRIMARY, linewidth=2.5, label=f'XGB-SVM Pipeline (AUC = {auc_val:.3f})')
            ax_roc.plot([0, 1], [0, 1], color='#64748b', linestyle='--', label='Random Chance (AUC = 0.50)')
            ax_roc.fill_between(fprs, tprs, alpha=0.15, color=COLOR_PRIMARY)
            ax_roc.set_title("Receiver Operating Characteristic (ROC)", fontsize=13, fontweight='bold', color='#f8fafc')
            ax_roc.set_xlabel("False Positive Rate", fontsize=10, color='#94a3b8')
            ax_roc.set_ylabel("True Positive Rate", fontsize=10, color='#94a3b8')
            ax_roc.legend(facecolor='#1e293b', edgecolor='#334155')
            ax_roc.grid(True)

            # PR
            precs = [p['precision'] for p in pr_pts]
            recs = [p['recall'] for p in pr_pts]
            ax_pr.plot(recs, precs, color=COLOR_ACCENT, linewidth=2.5, label=f'Precision-Recall (High Prec = {prec_val*100:.1f}%)')
            ax_pr.set_title("Precision-Recall Curve (Imbalanced Data)", fontsize=13, fontweight='bold', color='#f8fafc')
            ax_pr.set_xlabel("Recall", fontsize=10, color='#94a3b8')
            ax_pr.set_ylabel("Precision", fontsize=10, color='#94a3b8')
            ax_pr.legend(facecolor='#1e293b', edgecolor='#334155')
            ax_pr.grid(True)

            save_plot(fig, "roc_pr_curves.png")

        # 6. Feature Importance Barplot
        top_feats = m_data.get('top_features', [])
        if top_feats:
            print("[*] Generating Feature Importance Plot...")
            fig, ax = plt.subplots(figsize=(9, 5))
            f_names = [f['feature'].replace('num__', '').replace('cat__', '') for f in reversed(top_feats)]
            f_vals = [f['importance'] for f in reversed(top_feats)]
            y_pos = np.arange(len(f_names))

            bars = ax.barh(y_pos, f_vals, color=COLOR_PRIMARY, edgecolor='#475569')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(f_names, color='#e2e8f0', fontsize=10)
            ax.set_xlabel("XGBoost Relative Feature Importance", fontsize=11, color='#94a3b8')
            ax.set_title("Top 10 Fraud Detection Predictive Drivers", fontsize=14, fontweight='bold', pad=15, color='#f8fafc')
            ax.grid(axis='x')

            for bar in bars:
                w = bar.get_width()
                ax.text(w + 0.005, bar.get_y() + bar.get_height()/2, f"{w:.3f}",
                        va='center', color='#cbd5e1', fontsize=9, fontweight='bold')
            save_plot(fig, "feature_importance.png")

    print("[+] All EDA charts generated successfully!")


if __name__ == "__main__":
    run_eda()

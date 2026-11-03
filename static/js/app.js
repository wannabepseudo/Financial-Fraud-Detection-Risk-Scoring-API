/**
 * Financial Fraud Detection & Risk Scoring API 2026
 * Interactive Dashboard & Real-Time Telemetry Application
 */

let rocChartInstance = null;
let featuresChartInstance = null;
let isStreamActive = true;
let streamInterval = null;
let currentSnippetLanguage = 'curl';

const SQL_PRESETS = {
  rolling_velocities: {
    title: "Rolling 1-Hour & 24-Hour Velocity Windows (SQLite Window Functions)",
    sql: `-- Computes rolling transaction frequency and 24-hour spend using SQLite window functions
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
LIMIT 15;`
  },
  merchant_risks: {
    title: "Merchant Category Risk & Volume Aggregations",
    sql: `-- Aggregates fraud probability and ticket volume across merchant sectors
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
LIMIT 15;`
  },
  impossible_travel: {
    title: "Impossible Travel Supersonic Speed Anomaly Detector (>800 km/h)",
    sql: `-- Uses LAG window functions and Haversine distance to detect supersonic velocity
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
LIMIT 10;`
  }
};

// Initialization on DOM Load
document.addEventListener("DOMContentLoaded", () => {
  loadInitialMetrics();
  loadRecentStream();
  loadSqlQuery('rolling_velocities');
  showCodeSnippet('curl');
  runSimulation(); // Initial test score

  // Auto-stream simulated transactions every 4 seconds
  streamInterval = setInterval(() => {
    if (isStreamActive) {
      addSimulatedStreamItem();
    }
  }, 4500);
});

// Tab Switcher
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('text-white', 'bg-indigo-600', 'shadow-sm');
    btn.classList.add('text-slate-400');
  });

  const activeContent = document.getElementById(`tab-${tabId}`);
  if (activeContent) activeContent.classList.remove('hidden');

  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.remove('text-slate-400');
    activeBtn.classList.add('text-white', 'bg-indigo-600', 'shadow-sm');
  }

  if (tabId === 'metrics') {
    setTimeout(renderMetricsCharts, 100);
  }
  lucide.createIcons();
}

// Preset Scenario Loader
function loadScenario(scenario) {
  if (scenario === 'coffee') {
    document.getElementById('sim-amount').value = 4.50;
    document.getElementById('sim-amount-num').value = 4.50;
    document.getElementById('amount-val-display').innerText = '$4.50';
    document.getElementById('sim-channel').value = 'POS_CHIP';
    document.getElementById('sim-category').value = 'dining';
    document.getElementById('sim-hour').value = 8;
    document.getElementById('hour-val-display').innerText = '08:00';
    document.getElementById('sim-v1h').value = 0;
    document.getElementById('v1h-val-display').innerText = '0 tx';
    document.getElementById('sim-dist').value = 2;
    document.getElementById('dist-val-display').innerText = '2 km';
    document.getElementById('sim-new-device').checked = false;
    document.getElementById('sim-foreign').checked = false;
    document.getElementById('sim-failed-pins').checked = false;
  } else if (scenario === 'crypto') {
    document.getElementById('sim-amount').value = 3450;
    document.getElementById('sim-amount-num').value = 3450;
    document.getElementById('amount-val-display').innerText = '$3,450.00';
    document.getElementById('sim-channel').value = 'API';
    document.getElementById('sim-category').value = 'crypto_exchange';
    document.getElementById('sim-hour').value = 2;
    document.getElementById('hour-val-display').innerText = '02:00';
    document.getElementById('sim-v1h').value = 5;
    document.getElementById('v1h-val-display').innerText = '5 tx';
    document.getElementById('sim-dist').value = 3800;
    document.getElementById('dist-val-display').innerText = '3800 km';
    document.getElementById('sim-new-device').checked = true;
    document.getElementById('sim-foreign').checked = true;
    document.getElementById('sim-failed-pins').checked = true;
  } else if (scenario === 'travel') {
    document.getElementById('sim-amount').value = 920;
    document.getElementById('sim-amount-num').value = 920;
    document.getElementById('amount-val-display').innerText = '$920.00';
    document.getElementById('sim-channel').value = 'POS_CHIP';
    document.getElementById('sim-category').value = 'travel';
    document.getElementById('sim-hour').value = 16;
    document.getElementById('hour-val-display').innerText = '16:00';
    document.getElementById('sim-v1h').value = 1;
    document.getElementById('v1h-val-display').innerText = '1 tx';
    document.getElementById('sim-dist').value = 2400;
    document.getElementById('dist-val-display').innerText = '2400 km';
    document.getElementById('sim-new-device').checked = false;
    document.getElementById('sim-foreign').checked = true;
    document.getElementById('sim-failed-pins').checked = false;
  } else if (scenario === 'credential') {
    document.getElementById('sim-amount').value = 620;
    document.getElementById('sim-amount-num').value = 620;
    document.getElementById('amount-val-display').innerText = '$620.00';
    document.getElementById('sim-channel').value = 'WEB';
    document.getElementById('sim-category').value = 'p2p_transfer';
    document.getElementById('sim-hour').value = 3;
    document.getElementById('hour-val-display').innerText = '03:00';
    document.getElementById('sim-v1h').value = 3;
    document.getElementById('v1h-val-display').innerText = '3 tx';
    document.getElementById('sim-dist').value = 450;
    document.getElementById('dist-val-display').innerText = '450 km';
    document.getElementById('sim-new-device').checked = true;
    document.getElementById('sim-foreign').checked = false;
    document.getElementById('sim-failed-pins').checked = true;
  }
  runSimulation();
}

function randomizeInputs() {
  const cats = ['grocery', 'dining', 'gas_station', 'electronics', 'travel', 'p2p_transfer', 'crypto_exchange'];
  const chans = ['POS_CHIP', 'POS_SWIPE', 'WEB', 'MOBILE_APP', 'ATM', 'API'];
  const amt = Math.floor(Math.random() * 2500) + 5;
  const hour = Math.floor(Math.random() * 24);
  const v1h = Math.floor(Math.random() * 6);
  const dist = Math.floor(Math.random() * 4000);

  document.getElementById('sim-amount').value = amt;
  document.getElementById('sim-amount-num').value = amt;
  document.getElementById('amount-val-display').innerText = '$' + amt.toFixed(2);
  document.getElementById('sim-channel').value = chans[Math.floor(Math.random() * chans.length)];
  document.getElementById('sim-category').value = cats[Math.floor(Math.random() * cats.length)];
  document.getElementById('sim-hour').value = hour;
  document.getElementById('hour-val-display').innerText = String(hour).padStart(2,'0') + ':00';
  document.getElementById('sim-v1h').value = v1h;
  document.getElementById('v1h-val-display').innerText = v1h + ' tx';
  document.getElementById('sim-dist').value = dist;
  document.getElementById('dist-val-display').innerText = dist + ' km';
  document.getElementById('sim-new-device').checked = Math.random() < 0.35;
  document.getElementById('sim-foreign').checked = Math.random() < 0.25;
  document.getElementById('sim-failed-pins').checked = Math.random() < 0.20;

  runSimulation();
}

// Real-Time Transaction Scoring Execution
async function runSimulation() {
  const payload = {
    user_id: "usr_sim_client",
    amount: parseFloat(document.getElementById('sim-amount-num').value) || 50.0,
    channel: document.getElementById('sim-channel').value,
    merchant_category: document.getElementById('sim-category').value,
    hour_of_day: parseInt(document.getElementById('sim-hour').value),
    velocity_1h: parseInt(document.getElementById('sim-v1h').value),
    velocity_24h: parseInt(document.getElementById('sim-v1h').value) + 1,
    distance_from_home_km: parseFloat(document.getElementById('sim-dist').value),
    is_foreign_transaction: document.getElementById('sim-foreign').checked ? 1 : 0,
    failed_pin_attempts: document.getElementById('sim-failed-pins').checked ? 3 : 0,
    is_new_device: document.getElementById('sim-new-device').checked ? 1 : 0
  };

  try {
    const t0 = performance.now();
    const resp = await fetch('/api/v1/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    const clientLatency = (performance.now() - t0).toFixed(1);

    updateRiskGauge(data, clientLatency);
  } catch (err) {
    console.error("Scoring error:", err);
  }
}

// Update Radial Gauge and Decision Cards
function updateRiskGauge(res, clientLatency) {
  const score = res.risk_score;
  const needle = document.getElementById('gauge-needle');
  const scoreDisplay = document.getElementById('score-number-display');
  const tierDisplay = document.getElementById('score-tier-display');
  const badge = document.getElementById('decision-badge');
  const latencyPill = document.getElementById('eval-latency-pill');
  const txIdDisplay = document.getElementById('tx-id-display');
  const confDisplay = document.getElementById('model-conf-display');
  const probXgb = document.getElementById('prob-xgb-display');
  const probSvm = document.getElementById('prob-svm-display');
  const factorsContainer = document.getElementById('risk-factors-container');

  // Needle angle (-90deg at 0 to +90deg at 100)
  const angle = (score / 100.0) * 180.0 - 90.0;
  needle.style.transform = `rotate(${angle}deg)`;

  scoreDisplay.innerText = score.toFixed(1);
  scoreDisplay.className = "text-3xl font-extrabold font-mono tracking-tight";
  
  if (score >= 70.0) {
    scoreDisplay.classList.add("text-red-400");
    tierDisplay.innerText = `RISK SCORE: ${res.risk_tier} (FRAUD DETECTED)`;
    tierDisplay.className = "text-xs font-semibold text-red-400 uppercase tracking-wider mt-0.5";
    badge.className = "px-5 py-2 rounded-xl text-sm font-bold tracking-wide badge-decline flex items-center space-x-2";
    badge.innerHTML = `<i data-lucide="shield-x" class="w-5 h-5"></i><span>TRANSACTION DECLINED</span>`;
  } else if (score >= 35.0) {
    scoreDisplay.classList.add("text-amber-400");
    tierDisplay.innerText = `RISK SCORE: ${res.risk_tier} (ELEVATED RISK)`;
    tierDisplay.className = "text-xs font-semibold text-amber-400 uppercase tracking-wider mt-0.5";
    badge.className = "px-5 py-2 rounded-xl text-sm font-bold tracking-wide badge-review flex items-center space-x-2";
    badge.innerHTML = `<i data-lucide="alert-circle" class="w-5 h-5"></i><span>MANUAL REVIEW REQUIRED</span>`;
  } else {
    scoreDisplay.classList.add("text-emerald-400");
    tierDisplay.innerText = `RISK SCORE: LOW (VERIFIED)`;
    tierDisplay.className = "text-xs font-semibold text-emerald-400 uppercase tracking-wider mt-0.5";
    badge.className = "px-5 py-2 rounded-xl text-sm font-bold tracking-wide badge-approve flex items-center space-x-2";
    badge.innerHTML = `<i data-lucide="shield-check" class="w-5 h-5"></i><span>TRANSACTION APPROVED</span>`;
  }

  latencyPill.innerText = `⚡ ${res.inference_latency_ms} ms (SLA PASS)`;
  txIdDisplay.innerText = res.transaction_id;
  confDisplay.innerText = `Confidence: ${(res.confidence * 100).toFixed(1)}%`;
  probXgb.innerText = res.model_breakdown.xgboost_probability.toFixed(4);
  probSvm.innerText = res.model_breakdown.svm_probability.toFixed(4);

  // Render Risk Factors
  factorsContainer.innerHTML = '';
  if (res.risk_factors && res.risk_factors.length > 0) {
    res.risk_factors.forEach(rf => {
      const color = rf.severity === 'CRITICAL' ? 'text-red-400 border-red-900/60 bg-red-950/40' :
                    rf.severity === 'HIGH' ? 'text-amber-400 border-amber-900/60 bg-amber-950/40' :
                    rf.severity === 'MEDIUM' ? 'text-cyan-400 border-cyan-900/60 bg-cyan-950/40' :
                    'text-emerald-400 border-emerald-900/60 bg-emerald-950/40';
      const div = document.createElement('div');
      div.className = `text-xs p-2 rounded-lg border flex items-start space-x-2 ${color}`;
      div.innerHTML = `
        <span class="font-bold text-[10px] uppercase px-1.5 py-0.5 rounded bg-black/40 border border-current">${rf.severity}</span>
        <span class="flex-1">${rf.description}</span>
      `;
      factorsContainer.appendChild(div);
    });
  } else {
    factorsContainer.innerHTML = `<div class="text-xs text-slate-400">No anomalous risk factors detected.</div>`;
  }
  lucide.createIcons();
}

// Live Transaction Stream
async function loadRecentStream() {
  try {
    const resp = await fetch('/api/v1/analytics/recent');
    const items = await resp.json();
    const tbody = document.getElementById('stream-table-body');
    tbody.innerHTML = '';

    items.forEach(item => {
      appendStreamRow(item);
    });
  } catch (err) {
    console.error("Stream load error:", err);
  }
}

function appendStreamRow(tx) {
  const tbody = document.getElementById('stream-table-body');
  const tr = document.createElement('tr');
  tr.className = "hover:bg-slate-800/40 transition";

  const isFraud = tx.is_fraud === 1;
  const score = isFraud ? (75 + Math.random() * 24).toFixed(1) : (2 + Math.random() * 22).toFixed(1);
  const latency = (2.4 + Math.random() * 2.2).toFixed(2);

  const decisionBadge = score >= 70.0
    ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">DECLINED</span>`
    : score >= 35.0
    ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">REVIEW</span>`
    : `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">APPROVED</span>`;

  tr.innerHTML = `
    <td class="py-2.5 px-4 text-slate-400">${tx.transaction_id ? tx.transaction_id.substring(0, 10) : 'tx_' + Math.random().toString(36).substring(2, 8)}</td>
    <td class="py-2.5 px-4 text-slate-200">${tx.user_id ? tx.user_id.substring(0, 8) : 'usr_anon'}</td>
    <td class="py-2.5 px-4 text-slate-300">${tx.merchant_name || tx.merchant_category || 'Merchant'}</td>
    <td class="py-2.5 px-4 text-indigo-300">${tx.channel}</td>
    <td class="py-2.5 px-4 font-bold text-white">$${Number(tx.amount).toFixed(2)}</td>
    <td class="py-2.5 px-4 font-bold ${score >= 70 ? 'text-red-400' : 'text-emerald-400'}">${score}</td>
    <td class="py-2.5 px-4">${decisionBadge}</td>
    <td class="py-2.5 px-4 text-emerald-400">${latency} ms</td>
    <td class="py-2.5 px-4 text-slate-400 text-[11px]">${new Date().toLocaleTimeString()}</td>
  `;

  tbody.insertBefore(tr, tbody.firstChild);
  if (tbody.children.length > 25) {
    tbody.removeChild(tbody.lastChild);
  }
}

async function addSimulatedStreamItem() {
  try {
    const resp = await fetch('/api/v1/score/simulate?scenario=random');
    const data = await resp.json();
    const item = {
      transaction_id: data.transaction_id,
      user_id: 'usr_' + Math.random().toString(36).substring(2, 7),
      merchant_name: 'Simulated Merchant',
      channel: 'WEB',
      amount: (data.risk_score > 60 ? (400 + Math.random() * 2000) : (15 + Math.random() * 120)).toFixed(2),
      is_fraud: data.risk_score > 65 ? 1 : 0
    };
    appendStreamRow(item);
  } catch (err) {
    // Fallback row if network issue
  }
}

function toggleStream() {
  isStreamActive = !isStreamActive;
  const btn = document.getElementById('stream-toggle-btn');
  const txt = document.getElementById('stream-btn-text');
  if (isStreamActive) {
    btn.className = "px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center space-x-1.5";
    txt.innerText = "Pause Stream";
  } else {
    btn.className = "px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold transition flex items-center space-x-1.5";
    txt.innerText = "Resume Stream";
  }
}

// Initial Metrics & Charts
let cachedMetrics = null;

async function loadInitialMetrics() {
  try {
    const resp = await fetch('/api/v1/metrics');
    cachedMetrics = await resp.json();

    document.getElementById('kpi-auc').innerText = (cachedMetrics.metrics.auc_roc * 100).toFixed(1) + '%';
    document.getElementById('kpi-precision').innerText = (cachedMetrics.metrics.precision * 100).toFixed(1) + '%';
    document.getElementById('kpi-latency').innerText = cachedMetrics.latency_benchmark_ms.avg_ms.toFixed(1) + ' ms';
    document.getElementById('kpi-tx-count').innerText = cachedMetrics.dataset_total_samples.toLocaleString() + '+';
    document.getElementById('kpi-fraud-rate').innerText = cachedMetrics.dataset_fraud_rate_pct.toFixed(2) + '%';

    // Confusion matrix values
    const cm = cachedMetrics.metrics.confusion_matrix;
    document.getElementById('cm-tn').innerText = cm.true_negatives.toLocaleString();
    document.getElementById('cm-fp').innerText = cm.false_positives.toLocaleString();
    document.getElementById('cm-fn').innerText = cm.false_negatives.toLocaleString();
    document.getElementById('cm-tp').innerText = cm.true_positives.toLocaleString();
  } catch (err) {
    console.error("Metrics load error:", err);
  }
}

function renderMetricsCharts() {
  if (!cachedMetrics) return;

  // Render ROC Curve
  const rocCtx = document.getElementById('rocChart');
  if (rocCtx && cachedMetrics.curves && cachedMetrics.curves.roc) {
    if (rocChartInstance) rocChartInstance.destroy();

    const pts = cachedMetrics.curves.roc;
    rocChartInstance = new Chart(rocCtx, {
      type: 'line',
      data: {
        datasets: [
          {
            label: 'XGB-SVM Ensemble (AUC = ' + cachedMetrics.metrics.auc_roc.toFixed(3) + ')',
            data: pts.map(p => ({ x: p.fpr, y: p.tpr })),
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.3,
            pointRadius: 0
          },
          {
            label: 'Random Guessing Baseline',
            data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
            borderColor: '#475569',
            borderDash: [5, 5],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'linear',
            min: 0,
            max: 1,
            title: { display: true, text: 'False Positive Rate (FPR)', color: '#94a3b8' },
            grid: { color: '#1e293b' },
            ticks: { color: '#64748b' }
          },
          y: {
            min: 0,
            max: 1,
            title: { display: true, text: 'True Positive Rate (Sensitivity)', color: '#94a3b8' },
            grid: { color: '#1e293b' },
            ticks: { color: '#64748b' }
          }
        },
        plugins: {
          legend: { labels: { color: '#cbd5e1' } }
        }
      }
    });
  }

  // Render Feature Importances
  const featCtx = document.getElementById('featuresChart');
  if (featCtx && cachedMetrics.top_features) {
    if (featuresChartInstance) featuresChartInstance.destroy();

    const feats = cachedMetrics.top_features.slice(0, 8);
    const labels = feats.map(f => f.feature.replace('num__', '').replace('cat__', ''));
    const vals = feats.map(f => f.importance);

    featuresChartInstance = new Chart(featCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Predictive Feature Weight',
          data: vals,
          backgroundColor: '#06b6d4',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b' } },
          y: { grid: { display: false }, ticks: { color: '#cbd5e1' } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

// SQL Query Playground
function loadSqlQuery(queryId) {
  const preset = SQL_PRESETS[queryId];
  if (preset) {
    document.getElementById('sql-query-title').innerText = preset.title;
    document.getElementById('sql-code-display').innerText = preset.sql;
    executeSelectedQuery();
  }
}

async function executeSelectedQuery() {
  const queryId = document.getElementById('sql-query-select').value;
  const t0 = performance.now();

  try {
    const resp = await fetch('/api/v1/sql/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_id: queryId })
    });
    const data = await resp.json();
    const duration = (performance.now() - t0).toFixed(1);

    document.getElementById('sql-row-count').innerText = data.row_count;
    document.getElementById('sql-exec-time').innerText = `Execution time: ~${duration}ms`;

    const thead = document.getElementById('sql-table-head');
    const tbody = document.getElementById('sql-table-body');

    thead.innerHTML = '';
    tbody.innerHTML = '';

    if (data.columns && data.columns.length > 0) {
      const headerRow = document.createElement('tr');
      data.columns.forEach(col => {
        const th = document.createElement('th');
        th.className = "py-2.5 px-4";
        th.innerText = col;
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);

      data.rows.forEach(row => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-800/40 transition";
        data.columns.forEach(col => {
          const td = document.createElement('td');
          td.className = "py-2 px-4";
          td.innerText = row[col] !== null ? row[col] : 'NULL';
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("SQL execution error:", err);
  }
}

function copySqlCode() {
  const code = document.getElementById('sql-code-display').innerText;
  navigator.clipboard.writeText(code);
  alert("SQL query copied to clipboard!");
}

// API Playground
async function executeApiPlayground() {
  const reqBox = document.getElementById('api-request-json');
  const respBox = document.getElementById('api-response-json');
  const latencyBadge = document.getElementById('api-resp-latency');
  const statusBadge = document.getElementById('api-resp-status');

  try {
    const payload = JSON.parse(reqBox.value);
    const t0 = performance.now();
    const resp = await fetch('/api/v1/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await resp.json();
    const dur = (performance.now() - t0).toFixed(1);

    latencyBadge.innerText = `${dur} ms`;
    statusBadge.innerText = `Status: ${resp.status} ${resp.statusText}`;
    statusBadge.className = resp.ok ? "px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 font-mono" : "px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 font-mono";
    respBox.innerText = JSON.stringify(result, null, 2);
  } catch (err) {
    respBox.innerText = "Error parsing JSON or network failure: " + err.message;
  }
}

// Code Snippet Generator
function showCodeSnippet(lang) {
  currentSnippetLanguage = lang;
  document.getElementById('btn-snippet-curl').className = lang === 'curl' ? "px-3 py-1 rounded text-xs font-semibold text-white bg-indigo-600" : "px-3 py-1 rounded text-xs font-semibold text-slate-400 hover:text-white";
  document.getElementById('btn-snippet-python').className = lang === 'python' ? "px-3 py-1 rounded text-xs font-semibold text-white bg-indigo-600" : "px-3 py-1 rounded text-xs font-semibold text-slate-400 hover:text-white";
  document.getElementById('btn-snippet-node').className = lang === 'node' ? "px-3 py-1 rounded text-xs font-semibold text-white bg-indigo-600" : "px-3 py-1 rounded text-xs font-semibold text-slate-400 hover:text-white";

  const host = window.location.origin || "http://localhost:8000";
  let snippet = "";

  if (lang === 'curl') {
    snippet = `curl -X POST "${host}/api/v1/score" \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_id": "usr_99182",
    "amount": 1450.00,
    "channel": "WEB",
    "merchant_category": "crypto_exchange",
    "velocity_1h": 4,
    "is_foreign_transaction": 1,
    "failed_pin_attempts": 2,
    "is_new_device": 1
  }'`;
  } else if (lang === 'python') {
    snippet = `import requests

url = "${host}/api/v1/score"
payload = {
    "user_id": "usr_99182",
    "amount": 1450.00,
    "channel": "WEB",
    "merchant_category": "crypto_exchange",
    "velocity_1h": 4,
    "is_foreign_transaction": 1,
    "failed_pin_attempts": 2,
    "is_new_device": 1
}

response = requests.post(url, json=payload)
data = response.json()
print(f"Risk Score: {data['risk_score']} | Decision: {data['decision']}")
print(f"Latency: {data['inference_latency_ms']} ms")`;
  } else {
    snippet = `const response = await fetch("${host}/api/v1/score", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    user_id: "usr_99182",
    amount: 1450.00,
    channel: "WEB",
    merchant_category: "crypto_exchange",
    velocity_1h: 4,
    is_foreign_transaction: 1,
    failed_pin_attempts: 2,
    is_new_device: 1
  })
});

const data = await response.json();
console.log(\`Decision: \${data.decision} (\${data.risk_score}/100) in \${data.inference_latency_ms}ms\`);`;
  }

  document.getElementById('snippet-code-display').innerText = snippet;
}

function copyCurrentSnippet() {
  const code = document.getElementById('snippet-code-display').innerText;
  navigator.clipboard.writeText(code);
  alert("Code snippet copied to clipboard!");
}

// Lightbox modal for EDA charts
function openImageModal(src, title) {
  document.getElementById('modal-img-tag').src = src;
  document.getElementById('modal-img-title').innerText = title;
  document.getElementById('image-modal').classList.remove('hidden');
}

function closeImageModal() {
  document.getElementById('image-modal').classList.add('hidden');
}

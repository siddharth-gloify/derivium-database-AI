'use strict';

// ── DOM refs ──────────────────────────────────────────────────────────────────
const questionEl      = document.getElementById('question');
const runBtn          = document.getElementById('runBtn');
const copyBtn         = document.getElementById('copyBtn');

const sqlSection      = document.getElementById('sqlSection');
const sqlDisplay      = document.getElementById('sqlDisplay');
const metaSection     = document.getElementById('metaSection');
const validationBadge = document.getElementById('validationBadge');
const timingsEl       = document.getElementById('timingsEl');

const emptyState      = document.getElementById('emptyState');
const loadingState    = document.getElementById('loadingState');
const loadingMsg      = document.getElementById('loadingMsg');
const errorState      = document.getElementById('errorState');
const errorMsg        = document.getElementById('errorMsg');
const resultsState    = document.getElementById('resultsState');
const rowCountLabel   = document.getElementById('rowCountLabel');
const tableHead       = document.getElementById('tableHead');
const tableBody       = document.getElementById('tableBody');

// ── State ─────────────────────────────────────────────────────────────────────
let rawSQL = '';

// ── Helpers ───────────────────────────────────────────────────────────────────

function showPanel(el) {
  [emptyState, loadingState, errorState, resultsState].forEach(s => s.classList.add('hidden'));
  el.classList.remove('hidden');
}

function setLoading(on) {
  runBtn.disabled = on;
  runBtn.querySelector('.btn-text').textContent = on ? 'Running…' : 'Run Query';
  if (on) showPanel(loadingState);
}

function esc(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** Very lightweight SQL keyword highlighter. */
const KW  = /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|CROSS|ON|AND|OR|NOT|IN|IS|NULL|AS|DISTINCT|ORDER|BY|GROUP|HAVING|LIMIT|OFFSET|BETWEEN|LIKE|ILIKE|UNION|ALL|CASE|WHEN|THEN|ELSE|END|EXISTS|WITH|RETURNING|OVER|PARTITION|INTERVAL|DATE)\b/g;
const FNS = /\b(COUNT|SUM|AVG|MIN|MAX|COALESCE|NULLIF|CAST|TO_DATE|TO_CHAR|CURRENT_DATE|CURRENT_TIMESTAMP|NOW|EXTRACT|DATE_PART|DATE_TRUNC|GREATEST|LEAST|ROUND|FLOOR|CEIL|ABS|LENGTH|LOWER|UPPER|TRIM|CONCAT|STRING_AGG|ARRAY_AGG|ROW_NUMBER|RANK|DENSE_RANK|LAG|LEAD|FIRST_VALUE|LAST_VALUE)\b/g;
const STR = /'([^']*)'/g;

function highlightSQL(sql) {
  // Escape HTML first, then wrap tokens (order matters: strings > fns > kw)
  let h = esc(sql);
  h = h.replace(STR, "<span class='str'>'$1'</span>");
  h = h.replace(FNS, "<span class='fn'>$&</span>");
  h = h.replace(KW,  "<span class='kw'>$&</span>");
  return h;
}

function isNumericVal(v) {
  if (v === null || v === undefined || v === '') return false;
  return !isNaN(Number(v));
}

// ── Main query flow ───────────────────────────────────────────────────────────
async function runQuery() {
  const question = questionEl.value.trim();
  if (!question) {
    questionEl.focus();
    return;
  }

  setLoading(true);
  loadingMsg.textContent = 'Generating SQL…';

  // Reset left panel
  sqlSection.classList.add('hidden');
  metaSection.classList.add('hidden');

  // After a short delay, update loading message to indicate DB phase
  const phaseTimer = setTimeout(() => {
    loadingMsg.textContent = 'Executing query…';
  }, 2500);

  try {
    const resp = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    handleResult(data);
  } catch (err) {
    showPanel(errorState);
    errorMsg.textContent = `Network error: ${err.message}`;
  } finally {
    clearTimeout(phaseTimer);
    setLoading(false);
  }
}

function handleResult(data) {
  // ── Left panel ──────────────────────────────────────────────────────────────
  if (data.sql) {
    rawSQL = data.sql;
    sqlDisplay.innerHTML = highlightSQL(data.sql);
    sqlSection.classList.remove('hidden');
  }

  // Validation badge
  if (data.validated) {
    validationBadge.className = 'badge ok';
    validationBadge.innerHTML = '&#10003;&nbsp; Validated &mdash; read only';
  } else if (data.sql) {
    validationBadge.className = 'badge err';
    validationBadge.innerHTML = '&#10005;&nbsp; Blocked';
  } else {
    validationBadge.className = 'badge';
    validationBadge.textContent = '';
  }

  // Timings
  const llm   = data.llm_time  ?? 0;
  const db    = data.db_time   ?? 0;
  const total = llm + db;
  timingsEl.innerHTML = `
    <div class="t-row">
      <span class="t-label">LLM</span>
      <span class="t-val">${llm.toFixed(2)} s</span>
    </div>
    ${db > 0 ? `
    <div class="t-row">
      <span class="t-label">Database</span>
      <span class="t-val">${db.toFixed(2)} s</span>
    </div>` : ''}
    <div class="t-row t-total">
      <span class="t-label">Total</span>
      <span class="t-val">${total.toFixed(2)} s</span>
    </div>
  `;
  metaSection.classList.remove('hidden');

  // ── Right panel ─────────────────────────────────────────────────────────────
  if (data.error) {
    errorMsg.textContent = data.error;
    showPanel(errorState);
    return;
  }

  if (!data.rows || data.row_count === 0) {
    errorMsg.textContent = 'Query returned 0 rows.';
    errorMsg.className = 'state-msg';   // no red — not really an error
    showPanel(errorState);
    return;
  }

  renderTable(data.columns, data.rows, data.row_count);
}

function renderTable(cols, rows, count) {
  // Detect numeric columns (check first row)
  const isNum = {};
  cols.forEach(c => {
    isNum[c] = isNumericVal(rows[0][c]);
  });

  // Header
  tableHead.innerHTML =
    '<tr>' + cols.map(c =>
      `<th title="${esc(c)}">${esc(c)}</th>`
    ).join('') + '</tr>';

  // Body
  tableBody.innerHTML = rows.map(row =>
    '<tr>' + cols.map(c => {
      const raw = row[c];

      if (raw === null || raw === undefined) {
        return '<td class="td-null" title="NULL">null</td>';
      }

      if (typeof raw === 'boolean' || raw === true || raw === false) {
        const label = raw ? 'true' : 'false';
        return `<td class="td-bool"><span class="bool-${label}">${label}</span></td>`;
      }

      if (typeof raw === 'object') {
        const s = JSON.stringify(raw);
        return `<td title="${esc(s)}">${esc(s)}</td>`;
      }

      const s = String(raw);
      if (isNum[c]) {
        return `<td class="td-num" title="${esc(s)}">${esc(s)}</td>`;
      }

      return `<td title="${esc(s)}">${esc(s)}</td>`;
    }).join('') + '</tr>'
  ).join('');

  rowCountLabel.textContent =
    `${count.toLocaleString()} row${count !== 1 ? 's' : ''} returned`;

  showPanel(resultsState);
}

// ── Copy SQL ──────────────────────────────────────────────────────────────────
copyBtn.addEventListener('click', () => {
  if (!rawSQL) return;
  navigator.clipboard.writeText(rawSQL).then(() => {
    copyBtn.setAttribute('title', 'Copied!');
    setTimeout(() => copyBtn.setAttribute('title', 'Copy SQL'), 1600);
  });
});

// ── Event listeners ───────────────────────────────────────────────────────────
runBtn.addEventListener('click', runQuery);

questionEl.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    runQuery();
  }
});

// Auto-focus on load
questionEl.focus();

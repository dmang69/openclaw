/* OpenClaw — control surface + chat frontend */
'use strict';

// ── tab navigation ─────────────────────────────────────────────────────

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    const tab = item.dataset.tab;
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    item.classList.add('active');
    document.getElementById(`tab-${tab}`).classList.add('active');

    // Lazy-load tab data
    if (tab === 'control')    loadControl();
    if (tab === 'evidence')   loadEvidence();
    if (tab === 'chronology') loadChronology();
    if (tab === 'logs')       loadLogs();
    if (tab === 'safety')     loadSafety();
  });
});

// ── chat ───────────────────────────────────────────────────────────────

function currentPersona() {
  return document.getElementById('persona-select').value;
}

document.getElementById('persona-select').addEventListener('change', e => {
  document.getElementById('persona-badge').textContent = e.target.value.charAt(0).toUpperCase() + e.target.value.slice(1);
});

document.getElementById('chat-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

async function sendMessage() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  appendMessage('You', msg, 'user');

  const indicator = appendMessage(currentPersona(), '…', 'assistant typing-indicator');
  document.getElementById('send-btn').disabled = true;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, persona: currentPersona() }),
    });
    const data = await res.json();
    indicator.remove();
    if (data.error) {
      appendMessage('Error', data.error, 'error');
    } else {
      appendMessage(data.persona || currentPersona(), data.response, 'assistant');
      document.getElementById('backend-badge').textContent = data.backend || 'Local';
    }
  } catch (err) {
    indicator.remove();
    appendMessage('Error', String(err), 'error');
  } finally {
    document.getElementById('send-btn').disabled = false;
  }
}

function appendMessage(label, content, type) {
  const area = document.getElementById('chat-area');
  const div = document.createElement('div');
  div.className = `msg msg-${type.split(' ')[0]}`;
  const lbl = document.createElement('div');
  lbl.className = 'msg-label';
  lbl.textContent = label;
  const body = document.createElement('div');
  body.className = 'msg-content';
  body.textContent = content;
  div.appendChild(lbl);
  div.appendChild(body);
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
  return div;
}

async function resetChat() {
  await fetch('/api/chat/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ persona: currentPersona() }),
  });
  document.getElementById('chat-area').innerHTML = '';
}

// ── control surface ────────────────────────────────────────────────────

let controlData = {};

async function loadControl() {
  try {
    const res = await fetch('/api/control');
    controlData = await res.json();
    applyControlData(controlData);
    await loadSkillRows();
  } catch (e) {
    console.error('loadControl failed', e);
  }
}

function applyControlData(data) {
  // Checkboxes and selects with data-path
  document.querySelectorAll('[data-path]').forEach(el => {
    const val = getPath(data, el.dataset.path);
    if (val === undefined) return;
    if (el.type === 'checkbox') el.checked = Boolean(val);
    else if (el.tagName === 'SELECT') el.value = String(val);
    else if (el.type === 'number') el.value = val;
  });
}

function getPath(obj, path) {
  return path.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : undefined), obj);
}

function setPath(obj, path, value) {
  const keys = path.split('.');
  const last = keys.pop();
  const target = keys.reduce((o, k) => { if (!o[k]) o[k] = {}; return o[k]; }, obj);
  target[last] = value;
}

async function loadSkillRows() {
  try {
    const res = await fetch('/api/skills');
    const skills = await res.json();
    const container = document.getElementById('skill-rows');
    container.innerHTML = '';
    skills.forEach(skill => {
      const row = document.createElement('div');
      row.className = 'control-row';
      const label = document.createElement('label');
      label.textContent = skill.name.replace(/_/g, ' ');
      label.title = skill.description;
      const toggleLabel = document.createElement('label');
      toggleLabel.className = 'toggle';
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.dataset.path = `skills.enabled.${skill.name}`;
      input.checked = skill.enabled;
      const slider = document.createElement('span');
      slider.className = 'slider';
      toggleLabel.appendChild(input);
      toggleLabel.appendChild(slider);
      row.appendChild(label);
      row.appendChild(toggleLabel);
      container.appendChild(row);
    });
  } catch (e) {
    console.error('loadSkillRows failed', e);
  }
}

function toggleAdvanced(cb) {
  document.querySelectorAll('.advanced-only').forEach(el => {
    el.classList.toggle('hidden', !cb.checked);
  });
}

function collectControlData() {
  const data = JSON.parse(JSON.stringify(controlData));
  document.querySelectorAll('[data-path]').forEach(el => {
    let val;
    if (el.type === 'checkbox') val = el.checked;
    else if (el.type === 'number') val = Number(el.value);
    else val = el.value;
    setPath(data, el.dataset.path, val);
  });
  return data;
}

async function saveControl() {
  const data = collectControlData();
  const status = document.getElementById('save-status');
  try {
    const res = await fetch('/api/control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (res.ok) {
      controlData = await res.json();
      status.textContent = '✓ Saved';
      setTimeout(() => { status.textContent = ''; }, 2500);
    } else {
      const err = await res.json();
      status.style.color = 'var(--danger)';
      status.textContent = `Error: ${err.error}`;
    }
  } catch (e) {
    status.style.color = 'var(--danger)';
    status.textContent = String(e);
  }
}

// ── evidence ───────────────────────────────────────────────────────────

async function loadEvidence() {
  const el = document.getElementById('evidence-output');
  try {
    const res = await fetch('/api/evidence');
    const data = await res.json();
    el.textContent = data.result || '(empty)';
  } catch (e) {
    el.textContent = 'Error: ' + e;
  }
}

// ── chronology ─────────────────────────────────────────────────────────

async function loadChronology() {
  const el = document.getElementById('chronology-output');
  try {
    const res = await fetch('/api/chronology');
    const data = await res.json();
    el.textContent = data.result || '(empty)';
  } catch (e) {
    el.textContent = 'Error: ' + e;
  }
}

// ── logs ───────────────────────────────────────────────────────────────

async function loadLogs() {
  const level = document.getElementById('log-level-filter').value;
  const url = '/api/logs' + (level ? `?level=${level}` : '');
  try {
    const res = await fetch(url);
    const logs = await res.json();
    const stream = document.getElementById('log-stream');
    stream.innerHTML = '';
    logs.forEach(log => {
      const row = document.createElement('div');
      row.className = 'log-entry';
      row.innerHTML = `
        <span class="log-ts">${log.timestamp.slice(11, 19)}</span>
        <span class="log-level log-${log.level}">${log.level}</span>
        <span class="log-comp">${log.component || ''}</span>
        <span class="log-msg">${escHtml(log.message)}</span>
      `;
      stream.appendChild(row);
    });
    stream.scrollTop = stream.scrollHeight;
  } catch (e) {
    console.error('loadLogs failed', e);
  }
}

async function clearLogs() {
  await fetch('/api/logs/clear', { method: 'POST' });
  document.getElementById('log-stream').innerHTML = '';
}

// ── safety rules ───────────────────────────────────────────────────────

async function loadSafety() {
  const container = document.getElementById('safety-rules');
  try {
    const res = await fetch('/api/safety/rules');
    const rules = await res.json();
    container.innerHTML = rules.map(r => `
      <div class="safety-rule">
        <div class="safety-rule-id">${escHtml(r.id)}</div>
        <div class="safety-rule-desc">${escHtml(r.description)}</div>
      </div>
    `).join('');
  } catch (e) {
    container.textContent = 'Error loading safety rules: ' + e;
  }
}

// ── utilities ──────────────────────────────────────────────────────────

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Auto-refresh logs every 5 s when logs tab is active
setInterval(() => {
  if (document.getElementById('tab-logs').classList.contains('active')) {
    loadLogs();
  }
}, 5000);

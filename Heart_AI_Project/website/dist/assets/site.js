const API = "";

let sessionId = null;
let loading = false;
let glossaryItems = [];

const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const statusText = document.getElementById("status-text");
const progressBar = document.getElementById("progress-bar");
const progressPct = document.getElementById("progress-pct");

document.getElementById("year").textContent = new Date().getFullYear();

function md(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/\n/g, "<br>");
}

function addBubble(role, html, prediction) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.innerHTML = md(html);
  if (prediction?.risk_percentage != null) {
    const card = document.createElement("div");
    card.className = "risk-card";
    card.innerHTML = `<span class="risk-value">${prediction.risk_percentage}%</span><span class="risk-label">estimated cardiovascular risk</span>`;
    div.appendChild(card);
  }
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setProgress(collected) {
  const n = Object.keys(collected || {}).length;
  const pct = Math.round((n / 13) * 100);
  progressBar.style.width = `${pct}%`;
  progressPct.textContent = `${pct}%`;
}

async function loadMetrics() {
  const accEl = document.getElementById("metric-accuracy");
  const accSub = document.getElementById("metric-accuracy-sub");
  const aucEl = document.getElementById("metric-auc");
  const noteEl = document.getElementById("metrics-note");
  const listEl = document.getElementById("dataset-list");
  const heroAcc = document.getElementById("hero-accuracy");

  try {
    const res = await fetch(`${API}/api/metrics`);
    const m = await res.json();
    const acc = m.accuracy_percent ?? m.cleveland_benchmark_percent ?? "--";
    accEl.textContent = typeof acc === "number" ? `${acc}%` : acc;
    heroAcc.textContent = typeof acc === "number" ? `${acc}%` : "90%+";

    const cle = m.cleveland_benchmark_percent;
    const multi = m.test_accuracy_percent;
    accSub.textContent =
      cle && multi
        ? `Cleveland benchmark ${cle}% · Multi-center hold-out ${multi}%`
        : "Validated on held-out patients";

    if (m.roc_auc) aucEl.textContent = m.roc_auc;
    if (m.data?.total_records) {
      document.getElementById("metric-patients").textContent = m.data.total_records;
    }
    if (m.data?.datasets_merged) {
      document.getElementById("metric-datasets").textContent = m.data.datasets_merged;
    }

    if (m.data?.sources) {
      listEl.innerHTML = Object.entries(m.data.sources)
        .map(
          ([name, count]) =>
            `<li><strong>${name}</strong><span>${count} patients</span></li>`
        )
        .join("");
    }

    if (m.note) noteEl.textContent = m.note;
    if (m.meets_90_percent_goal) {
      accEl.parentElement.classList.add("metric-success");
    }
  } catch {
    accSub.textContent = "Run python train_model.py to refresh metrics.";
  }
}

function renderGlossary(filter = "") {
  const grid = document.getElementById("glossary-grid");
  const q = filter.trim().toLowerCase();
  const items = glossaryItems.filter(
    (item) =>
      !q ||
      item.term.toLowerCase().includes(q) ||
      item.plain.toLowerCase().includes(q)
  );

  grid.innerHTML = items
    .map(
      (item) => `
      <article class="glossary-card">
        <h3>${item.term}</h3>
        <p>${item.plain}</p>
      </article>`
    )
    .join("");

  if (!items.length) {
    grid.innerHTML = `<p class="glossary-empty">No terms match "${filter}".</p>`;
  }
}

async function loadGlossary() {
  try {
    const res = await fetch(`${API}/api/glossary`);
    glossaryItems = await res.json();
  } catch {
    const res = await fetch(`${API}/assets/glossary.json`);
    glossaryItems = await res.json();
  }
  renderGlossary();
  document.getElementById("glossary-search").addEventListener("input", (e) => {
    renderGlossary(e.target.value);
  });
}

async function checkHealth() {
  try {
    const res = await fetch(`${API}/api/health`);
    const data = await res.json();
    const ok = data.model_loaded === true;
    statusText.textContent = ok ? "Model online" : "Model offline";
    return ok;
  } catch {
    statusText.textContent = "Model offline";
    return false;
  }
}

async function sendMessage(text) {
  const trimmed = text.trim();
  if (!trimmed || loading) return;

  loading = true;
  input.disabled = true;
  addBubble("user", trimmed);

  try {
    const res = await fetch(`${API}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmed, session_id: sessionId }),
    });
    if (!res.ok) throw new Error("fail");
    const data = await res.json();
    sessionId = data.session_id;
    setProgress(data.collected);
    addBubble("bot", data.reply, data.prediction);
    statusText.textContent = "Model online";
  } catch {
    addBubble(
      "bot",
      "Sorry - I could not reach the server. Run **RUN_WEBSITE.bat**, then refresh."
    );
    statusText.textContent = "Model offline";
  } finally {
    loading = false;
    input.disabled = false;
    input.focus();
  }
}

async function initChat() {
  await checkHealth();
  try {
    const res = await fetch(`${API}/api/chat/welcome`);
    const data = await res.json();
    sessionId = data.session_id;
    addBubble("bot", data.reply);
    setProgress(data.collected);
  } catch {
    addBubble(
      "bot",
      "Welcome to **CardioRisk AI**! Start the backend, then refresh. Type **start** when ready."
    );
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const v = input.value;
  input.value = "";
  sendMessage(v);
});

document.querySelectorAll(".quick-btn").forEach((btn) => {
  btn.addEventListener("click", () => sendMessage(btn.dataset.cmd));
});

loadMetrics();
loadGlossary();
initChat();

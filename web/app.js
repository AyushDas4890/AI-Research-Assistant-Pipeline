const $ = (s) => document.querySelector(s);
const AGENTS = ["planner", "searcher", "reader", "critic", "writer"];
const ICON = { planner: "🧭", searcher: "🔎", reader: "📖", critic: "🧪", writer: "✍️" };

let currentReport = "";
let currentTitle = "";
let es = null;

// ---------- pipeline rendering ----------
function renderPipeline(agents) {
  const track = $("#pipelineTrack");
  track.innerHTML = "";
  agents.forEach((a, i) => {
    const el = document.createElement("div");
    el.className = "pnode";
    el.id = `pnode-${a.node}`;
    el.innerHTML = `
      <div class="pn-idx">0${i + 1}</div>
      <div class="pn-name">${ICON[a.node] || ""} ${a.label}
        <span class="pn-spin"></span><span class="pn-check">✓</span></div>
      <div class="pn-desc" id="pdesc-${a.node}">${a.desc || ""}</div>`;
    track.appendChild(el);
  });
}

function setActive(node) {
  AGENTS.forEach((n) => {
    const el = $(`#pnode-${n}`);
    if (!el) return;
    if (n === node) el.classList.add("active");
  });
}

function setDone(node, descText) {
  const el = $(`#pnode-${node}`);
  if (!el) return;
  el.classList.remove("active");
  el.classList.add("done");
  if (descText) $(`#pdesc-${node}`).textContent = descText;
}

// ---------- stats ----------
function bumpStat(key, val) {
  const stat = document.querySelector(`.stat[data-k="${key}"]`);
  if (!stat) return;
  stat.querySelector(".stat-val").textContent = val;
  stat.classList.remove("bump");
  void stat.offsetWidth;
  stat.classList.add("bump");
}

// ---------- log ----------
function pushLog(lines) {
  const box = $("#logBox");
  (lines || []).forEach((line) => {
    const div = document.createElement("div");
    div.className = "log-line";
    div.innerHTML = line.replace(/^(\[[A-Z]+\])/, "<b>$1</b>");
    box.appendChild(div);
  });
  box.scrollTop = box.scrollHeight;
}

// ---------- run ----------
function runResearch(query) {
  if (!query.trim()) return;
  if (es) es.close();

  currentReport = "";
  $("#runBtn").disabled = true;
  $("#emptyState").classList.add("hidden");
  $("#reportCard").classList.add("hidden");
  $("#memoryBanner").classList.add("hidden");
  $("#pipeline").classList.remove("hidden");
  $("#workspace").classList.remove("hidden");
  $("#logBox").innerHTML = "";
  ["subq", "results", "insights", "retries", "time"].forEach((k) => bumpStat(k, "—"));

  es = new EventSource(`/api/research/stream?query=${encodeURIComponent(query)}`);

  es.addEventListener("start", (e) => {
    const d = JSON.parse(e.data);
    currentTitle = d.query;
    renderPipeline(d.agents);
    if (d.has_memory) $("#memoryBanner").classList.remove("hidden");
    setActive("planner");
  });

  es.addEventListener("agent", (e) => {
    const d = JSON.parse(e.data);
    pushLog(d.log);

    if (d.node === "planner") {
      bumpStat("subq", (d.sub_questions || []).length);
      setDone("planner", d.strategy || "Plan ready");
      setActive("searcher");
    } else if (d.node === "searcher") {
      bumpStat("results", d.results ?? 0);
      setDone("searcher", `${d.results ?? 0} sources`);
      setActive("reader");
    } else if (d.node === "reader") {
      bumpStat("insights", d.insights ?? 0);
      setDone("reader", `${d.insights ?? 0} insights`);
      setActive("critic");
    } else if (d.node === "critic") {
      bumpStat("retries", d.retry_count ?? 0);
      const verdict = d.gaps_found ? "Gaps → re-searching" : "Coverage OK";
      setDone("critic", verdict);
      setActive(d.gaps_found ? "searcher" : "writer");
    } else if (d.node === "writer") {
      setDone("writer", `${d.words ?? 0} words`);
    }
  });

  es.addEventListener("done", (e) => {
    const d = JSON.parse(e.data);
    currentReport = d.report || "";
    bumpStat("time", `${d.elapsed}s`);
    showReport(currentTitle, currentReport);
    AGENTS.forEach((n) => setDone(n));
    $("#runBtn").disabled = false;
    es.close();
    loadHistory();
  });

  es.addEventListener("error", (e) => {
    let msg = "Stream error";
    try { msg = JSON.parse(e.data).message; } catch (_) {}
    pushLog([`[ERROR] ${msg}`]);
    $("#runBtn").disabled = false;
    if (es) es.close();
  });
}

// ---------- report ----------
function showReport(title, md) {
  $("#reportTitle").textContent = title;
  $("#reportBody").innerHTML = marked.parse(md || "_No report produced._");
  $("#reportCard").classList.remove("hidden");
  $("#reportCard").scrollIntoView({ behavior: "smooth", block: "start" });
}

function downloadReport() {
  if (!currentReport) return;
  const blob = new Blob([currentReport], { type: "text/markdown" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = (currentTitle || "research_report").replace(/[^a-z0-9]+/gi, "_").slice(0, 50) + ".md";
  a.click();
  URL.revokeObjectURL(a.href);
}

// ---------- history ----------
async function loadHistory() {
  try {
    const res = await fetch("/api/sessions");
    const data = await res.json();
    const list = $("#historyList");
    if (!data.length) { list.innerHTML = '<div class="history-empty">No sessions yet</div>'; return; }
    list.innerHTML = "";
    data.forEach((s) => {
      const btn = document.createElement("button");
      btn.className = "history-item";
      const t = (s.timestamp || "").slice(0, 16).replace("T", " ");
      btn.innerHTML = `${escapeHtml(s.query)}<span class="hi-time">${t}</span>`;
      btn.onclick = () => openSession(s.id);
      list.appendChild(btn);
    });
  } catch (_) {}
}

async function openSession(id) {
  try {
    const res = await fetch(`/api/report/${id}`);
    const d = await res.json();
    currentReport = d.report || "";
    currentTitle = d.query || "Saved report";
    $("#emptyState").classList.add("hidden");
    showReport(currentTitle, currentReport);
  } catch (_) {}
}

function escapeHtml(s) {
  return (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// ---------- wire up ----------
$("#searchForm").addEventListener("submit", (e) => {
  e.preventDefault();
  runResearch($("#queryInput").value);
});
$("#chips").addEventListener("click", (e) => {
  if (e.target.classList.contains("chip")) {
    $("#queryInput").value = e.target.textContent;
    runResearch(e.target.textContent);
  }
});
$("#downloadBtn").addEventListener("click", downloadReport);
$("#copyBtn").addEventListener("click", () => {
  navigator.clipboard.writeText(currentReport || "");
  $("#copyBtn").textContent = "Copied ✓";
  setTimeout(() => ($("#copyBtn").textContent = "Copy"), 1500);
});
$("#newBtn").addEventListener("click", () => {
  $("#queryInput").value = "";
  $("#queryInput").focus();
  $("#reportCard").classList.add("hidden");
  $("#pipeline").classList.add("hidden");
  $("#workspace").classList.add("hidden");
  $("#emptyState").classList.remove("hidden");
});

loadHistory();

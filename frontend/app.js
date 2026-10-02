const API = "/api";
const $ = (id) => document.getElementById(id);
const createView = $("createView");
const detailView = $("detailView");
const historyList = $("historyList");
const optionsGrid = $("optionsGrid");
let currentDecisionId = null;

function showToast(message) {
  const el = $("toast");
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => el.classList.remove("show"), 2600);
}

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  let payload = null;
  try { payload = await response.json(); } catch (_) {}
  if (!response.ok) {
    throw new Error(payload?.error || payload?.message || `Request failed (${response.status})`);
  }
  return payload;
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
  }[char]));
}

function readableDate(value) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleString();
}

function showCreate() {
  currentDecisionId = null;
  createView.classList.add("active");
  detailView.classList.remove("active");
  loadHistory();
}

function showDetail() {
  createView.classList.remove("active");
  detailView.classList.add("active");
}

async function loadHistory() {
  historyList.innerHTML = '<div class="empty">Loading decisions…</div>';
  try {
    const decisions = await request("/decisions");
    if (!decisions.length) {
      historyList.innerHTML = '<div class="empty">No saved decisions yet.</div>';
      return;
    }
    historyList.innerHTML = decisions.map((decision) => `
      <button class="history-item" data-decision-id="${escapeHtml(decision.id)}" type="button">
        <span class="history-title">${escapeHtml(decision.title)}</span>
        <span class="history-date">${escapeHtml(readableDate(decision.created_at))}</span>
      </button>
    `).join("");
    historyList.querySelectorAll("[data-decision-id]").forEach((button) => {
      button.addEventListener("click", () => openDecision(button.dataset.decisionId));
    });
  } catch (error) {
    historyList.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
  }
}

async function openDecision(id) {
  try {
    const decision = await request(`/decisions/${id}`);
    currentDecisionId = decision.id;
    $("detailTitle").textContent = decision.title;
    const selected = (decision.options || []).find((option) => option.is_selected);
    $("finalChoiceText").textContent = selected ? `Final choice: ${selected.title}` : "No final choice selected yet.";
    renderOptions(decision.options || []);
    showDetail();
  } catch (error) {
    showToast(error.message);
  }
}

function renderOptions(options) {
  if (!options.length) {
    optionsGrid.innerHTML = '<div class="panel empty">No options yet. Add at least two options to compare.</div>';
    return;
  }

  optionsGrid.innerHTML = options.map((option) => {
    const pros = (option.pros_and_cons || []).filter((item) => item.type === "pro");
    const cons = (option.pros_and_cons || []).filter((item) => item.type === "con");
    return `
      <article class="option-card ${option.is_selected ? "selected" : ""}">
        <div class="option-top">
          <div>
            <h3 class="option-title">${escapeHtml(option.title)}</h3>
            ${option.is_selected ? '<span class="selected-badge">Final choice</span>' : ""}
          </div>
          <button class="danger-btn delete-option" data-option-id="${escapeHtml(option.id)}" type="button">Remove</button>
        </div>
        <div class="procon-columns">
          ${renderProConBox(option.id, "pro", "Pros", pros)}
          ${renderProConBox(option.id, "con", "Cons", cons)}
        </div>
        <button class="choose-btn" data-option-id="${escapeHtml(option.id)}" type="button">
          ${option.is_selected ? "Selected" : "Choose this option"}
        </button>
      </article>
    `;
  }).join("");

  optionsGrid.querySelectorAll(".delete-option").forEach((button) => {
    button.addEventListener("click", async () => {
      if (!confirm("Remove this option and its pros/cons?")) return;
      try {
        await request(`/options/${button.dataset.optionId}`, { method: "DELETE" });
        await openDecision(currentDecisionId);
      } catch (error) { showToast(error.message); }
    });
  });

  optionsGrid.querySelectorAll(".choose-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await request(`/decisions/${currentDecisionId}/select`, {
          method: "POST",
          body: JSON.stringify({ option_id: button.dataset.optionId }),
        });
        await openDecision(currentDecisionId);
      } catch (error) { showToast(error.message); }
    });
  });

  optionsGrid.querySelectorAll(".mini-form").forEach((form) => {
    form.addEventListener("submit", addProCon);
  });

  optionsGrid.querySelectorAll(".delete-pc").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await request(`/pros-cons/${button.dataset.pcId}`, { method: "DELETE" });
        await openDecision(currentDecisionId);
      } catch (error) { showToast(error.message); }
    });
  });
}

function renderProConBox(optionId, type, heading, items) {
  return `
    <div class="procon-box ${type}">
      <h4>${heading}</h4>
      <div class="item-list">
        ${items.length ? items.map((item) => `
          <div class="pc-item">
            <span>${escapeHtml(item.text)}</span>
            <button class="icon-btn delete-pc" data-pc-id="${escapeHtml(item.id)}" type="button" aria-label="Delete">×</button>
          </div>
        `).join("") : '<div class="muted">None yet</div>'}
      </div>
      <form class="mini-form" data-option-id="${escapeHtml(optionId)}" data-type="${type}">
        <input name="text" maxlength="1000" placeholder="Add ${type}" required />
        <button type="submit">Add</button>
      </form>
    </div>
  `;
}

async function addProCon(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const input = form.elements.text;
  try {
    await request(`/options/${form.dataset.optionId}/pros-cons`, {
      method: "POST",
      body: JSON.stringify({ type: form.dataset.type, text: input.value.trim() }),
    });
    input.value = "";
    await openDecision(currentDecisionId);
  } catch (error) { showToast(error.message); }
}

$("createDecisionForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("decisionTitle");
  try {
    const decision = await request("/decisions", {
      method: "POST",
      body: JSON.stringify({ title: input.value.trim() }),
    });
    input.value = "";
    await openDecision(decision.id);
  } catch (error) { showToast(error.message); }
});

$("addOptionForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentDecisionId) return;
  const input = $("optionTitle");
  try {
    await request(`/decisions/${currentDecisionId}/options`, {
      method: "POST",
      body: JSON.stringify({ title: input.value.trim() }),
    });
    input.value = "";
    await openDecision(currentDecisionId);
  } catch (error) { showToast(error.message); }
});

$("deleteDecisionBtn").addEventListener("click", async () => {
  if (!currentDecisionId || !confirm("Delete this decision and all of its data?")) return;
  try {
    await request(`/decisions/${currentDecisionId}`, { method: "DELETE" });
    showCreate();
  } catch (error) { showToast(error.message); }
});

$("backBtn").addEventListener("click", showCreate);
$("newDecisionBtn").addEventListener("click", showCreate);
$("refreshHistoryBtn").addEventListener("click", loadHistory);

loadHistory();

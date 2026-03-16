const API = "https://tejas1102-coding-coach-backend.hf.space/api";

let sidebar = null;
let currentResult = null;
let isSaved = false;

// ── Wait for LeetCode editor to load ─────────────────────
function waitForEditor(callback, attempts = 0) {
  if (attempts > 30) return;
  const editor = document.querySelector(".view-lines");
  if (editor) {
    callback();
  } else {
    setTimeout(() => waitForEditor(callback, attempts + 1), 1000);
  }
}

// ── Get code from Monaco editor on LeetCode ───────────────
function getCodeFromEditor() {
  const lines = document.querySelectorAll(".view-lines .view-line");
  if (!lines.length) return null;
  return Array.from(lines)
    .map((l) => l.textContent)
    .join("\n");
}

// ── Get problem name from page ────────────────────────────
function getProblemName() {
  const el =
    document.querySelector('[data-cy="question-title"]') ||
    document.querySelector(".text-title-large a") ||
    document.querySelector("h4 a") ||
    document.querySelector("title");
  return el
    ? el.textContent.trim().replace(" - LeetCode", "")
    : "Unknown Problem";
}

// ── Get language ──────────────────────────────────────────
function getLanguage() {
  const selectors = [
    '[data-cy="lang-select"]',
    'button[id*="headlessui-listbox-button"]',
    ".ant-select-selection-item",
    '[class*="language"] button',
    'button[class*="lang"]',
  ];

  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) {
      const text = el.textContent.toLowerCase();
      if (text.includes("java") && !text.includes("javascript")) return "java";
      if (text.includes("javascript")) return "javascript";
      if (text.includes("python")) return "python";
      if (text.includes("c++") || text.includes("cpp")) return "cpp";
      if (text.includes("c#")) return "csharp";
    }
  }

  const pageText = document.body.innerText.toLowerCase();
  if (
    pageText.includes("public class solution") ||
    pageText.includes("class solution {")
  )
    return "java";

  return "python";
}

// ── Create sidebar ────────────────────────────────────────
function createSidebar() {
  if (document.getElementById("coding-coach-sidebar")) return;

  sidebar = document.createElement("div");
  sidebar.id = "coding-coach-sidebar";
  sidebar.innerHTML = `
    <div id="cc-header">
      <h2>⚡ Coding Coach</h2>
      <button id="cc-close">✕</button>
    </div>
    <div id="cc-content">
      <div class="cc-loading">
        <span class="cc-loading-spinner">⚙️</span>
        <div>Analyzing your code...</div>
      </div>
    </div>
  `;

  document.body.appendChild(sidebar);

  document.getElementById("cc-close").addEventListener("click", () => {
    sidebar.classList.remove("open");
  });
}

// ── Inject analyze button into LeetCode ───────────────────
function injectButton() {
  if (document.getElementById("coding-coach-btn")) return;

  const btn = document.createElement("button");
  btn.id = "coding-coach-btn";
  btn.innerHTML = "⚡ Coding Coach";

  btn.addEventListener("click", () => {
    analyzeCode();
  });

  const selectors = [
    ".relative.flex.gap-2",
    '[class*="RunCode"]',
    ".flex.gap-2.items-center",
    "nav .flex",
  ];

  let inserted = false;
  for (const sel of selectors) {
    const toolbar = document.querySelector(sel);
    if (toolbar) {
      toolbar.appendChild(btn);
      inserted = true;
      break;
    }
  }

  if (!inserted) {
    btn.style.cssText = `
      position: fixed;
      bottom: 80px;
      right: 20px;
      z-index: 99998;
    `;
    document.body.appendChild(btn);
  }
}

// ── Main analyze function ─────────────────────────────────
async function analyzeCode() {
  const code = getCodeFromEditor();
  if (!code || code.trim().length < 10) {
    alert(
      "Could not read code from editor. Please make sure you have written some code.",
    );
    return;
  }

  const problemName = getProblemName();
  const language = getLanguage();
  console.log("Coding Coach detected language:", language);

  createSidebar();
  sidebar = document.getElementById("coding-coach-sidebar");
  sidebar.classList.add("open");
  isSaved = false;
  currentResult = null;

  document.getElementById("cc-content").innerHTML = `
    <div class="cc-loading">
      <span class="cc-loading-spinner">⚙️</span>
      <div style="color: #94a3b8; margin-bottom: 4px;">Analyzing your code...</div>
      <div style="color: #475569; font-size: 11px;">${problemName}</div>
    </div>
  `;

  try {
    const response = await fetch(`${API}/analyze-only`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language, problem_name: problemName }),
    });

    if (!response.ok) throw new Error("API error");
    const data = await response.json();
    currentResult = data;
    renderResults(data, problemName, language, code);
  } catch (err) {
    document.getElementById("cc-content").innerHTML = `
      <div class="cc-error">
        ❌ Could not connect to Coding Coach backend.<br><br>
        Make sure your FastAPI server is running at <strong>http://127.0.0.1:8000</strong>
      </div>
    `;
  }
}

// ── Render results in sidebar ─────────────────────────────
function renderResults(data, problemName, language, code) {
  const approach = data.approach_detection;
  const analysis = data.analysis;

  const difficultyText = analysis.difficulty_level.toLowerCase();
  const difficultyClass = difficultyText.includes("advanced")
    ? "advanced"
    : difficultyText.includes("intermediate")
      ? "intermediate"
      : "beginner";

  const tipsHTML = analysis.optimization_tips
    .map(
      (tip, i) => `
    <div class="cc-tip">
      <span class="cc-tip-num">${i + 1}.</span>
      <span class="cc-tip-text">${tip}</span>
    </div>
  `,
    )
    .join("");

  const goodHTML = analysis.good_practices
    .map(
      (p) => `
    <div class="cc-good">
      <span class="cc-good-check">✓</span>
      <span class="cc-good-text">${p}</span>
    </div>
  `,
    )
    .join("");

  document.getElementById("cc-content").innerHTML = `
    <div id="cc-save-area">
      <button class="cc-save-btn" id="cc-save-btn">💾 Save to History</button>
    </div>

    <div class="cc-section">
      <div class="cc-section-title">🎯 Approach Detected</div>
      <span class="cc-approach">${approach.predicted_approach}</span>
    </div>

    <div class="cc-section">
      <div class="cc-section-title">🧠 Approach Explanation</div>
      <div class="cc-explanation">${analysis.approach_explanation}</div>
    </div>

    <div class="cc-section">
      <div class="cc-section-title">⏱️ Complexity</div>
      <div class="cc-complexity-item">
        <div class="cc-complexity-label">Time</div>
        <div class="cc-complexity-value">${analysis.time_complexity}</div>
      </div>
      <div class="cc-complexity-item">
        <div class="cc-complexity-label">Space</div>
        <div class="cc-complexity-value">${analysis.space_complexity}</div>
      </div>
      <div class="cc-complexity-item">
        <div class="cc-complexity-label">Difficulty</div>
        <span class="cc-difficulty ${difficultyClass}">
          ${
            difficultyText.includes("advanced")
              ? "Advanced"
              : difficultyText.includes("intermediate")
                ? "Intermediate"
                : "Beginner"
          }
        </span>
      </div>
    </div>

    <div class="cc-section">
      <div class="cc-section-title">🚀 Optimization Tips</div>
      ${tipsHTML}
    </div>

    <div class="cc-section">
      <div class="cc-section-title">✅ Good Practices</div>
      ${goodHTML}
    </div>
  `;

  document.getElementById("cc-save-btn").addEventListener("click", async () => {
    const saveBtn = document.getElementById("cc-save-btn");
    saveBtn.disabled = true;
    saveBtn.textContent = "💾 Saving...";

    try {
      const res = await fetch(`${API}/save-submission`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language, problem_name: problemName }),
      });
      if (!res.ok) throw new Error("Save failed");
      saveBtn.textContent = "✅ Saved!";
      const saveArea = document.getElementById("cc-save-area");
      const msg = document.createElement("div");
      msg.className = "cc-saved-msg";
      msg.textContent = "Saved to history and score updated!";
      saveArea.appendChild(msg);
    } catch (err) {
      saveBtn.disabled = false;
      saveBtn.textContent = "💾 Save to History";
      alert("Failed to save. Make sure backend is running.");
    }
  });
}

// ── Init ──────────────────────────────────────────────────
waitForEditor(() => {
  setTimeout(injectButton, 2000);
});

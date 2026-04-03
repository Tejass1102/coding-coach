const API = "http://127.0.0.1:8000/api";

let sidebar = null;
let currentResult = null;
let isSaved = false;
let lastVerdict = null;

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
  lastVerdict = null;

  document.getElementById("cc-content").innerHTML = `
  <div class="cc-loading">
    <span class="cc-loading-spinner">⚙️</span>
    <div style="color: #94a3b8;">Analyzing your code...</div>
    <div style="color: #475569; font-size: 11px;">
      First load may take ~30 seconds to wake up server
    </div>
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
  const displayedApproach = analysis.final_approach || approach.predicted_approach;

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
      <button id="cc-check-btn" style="
        width:100%;
        margin-top:8px;
        background: #1e3a5f;
        border: 1px solid #3b82f6;
        color: #60a5fa;
        font-size:13px;
        font-weight:600;
        padding:8px;
        border-radius:10px;
        cursor:pointer;
      ">🔍 Check Result</button>
    </div>

    <div id="cc-verdict-area"></div>

    <div class="cc-section">
      <div class="cc-section-title">🎯 Approach Detected</div>
      <span class="cc-approach">${displayedApproach}</span>
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
          ${difficultyText.includes("advanced")
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

  // ── Save button listener ──────────────────────────────────
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

  // ── Check Result button listener (independent of save) ────
  document.getElementById("cc-check-btn").addEventListener("click", () => {
    const verdict = scanPageForVerdict();
    if (verdict) {
      renderVerdict(verdict);
    } else {
      const verdictArea = document.getElementById("cc-verdict-area");
      if (verdictArea)
        verdictArea.innerHTML = `
        <div style="color:#94a3b8; font-size:12px; text-align:center; padding:10px;">
          No result found yet. Please Run or Submit your code first.
        </div>`;
    }
  });

  // Auto-check the result on screen immediately after rendering the sidebar
  // so verdict appears right away without requiring a manual button click
  setTimeout(() => {
    const checkBtn = document.getElementById("cc-check-btn");
    if (checkBtn) checkBtn.click();
  }, 150);
}

// ── Broad verdict scan across entire result panel ─────────
function scanPageForVerdict() {
  // Try specific selectors first (fast path)
  const specificSelectors = [
    '[data-e2e-locator="submission-result"]',
    '[data-e2e-locator="console-result"]',
    ".text-green-s",
    ".text-red-s",
    '[class*="result__"]',
    '[class*="ResultBar"]',
    '[class*="status-"]',
  ];
  for (const sel of specificSelectors) {
    const el = document.querySelector(sel);
    if (el && el.textContent.trim()) {
      const verdict = classifyVerdict(el.textContent.trim());
      if (verdict) return verdict;
    }
  }

  // Broad fallback: scan all text in the result/console panel
  // Look for the parent container that holds the test result output
  const panelSelectors = [
    '[class*="console"]',
    '[class*="result"]',
    '[class*="testcase"]',
    '[class*="TestResult"]',
    '[class*="submission"]',
  ];
  for (const pSel of panelSelectors) {
    const panels = document.querySelectorAll(pSel);
    for (const panel of panels) {
      // Skip the coding coach sidebar itself
      if (panel.closest("#coding-coach-sidebar")) continue;
      const text = panel.textContent.trim();
      if (text.length > 3 && text.length < 500) {
        const verdict = classifyVerdict(text);
        if (verdict) return verdict;
      }
    }
  }
  return null;
}

// ── Classify verdict text ─────────────────────────────────
function classifyVerdict(text) {
  const t = text.toLowerCase();
  if (t.includes("accepted")) return "accepted";
  if (t.includes("wrong answer")) return "wrong_answer";
  if (t.includes("time limit")) return "time_limit_exceeded";
  if (t.includes("memory limit")) return "memory_limit_exceeded";
  if (t.includes("runtime error")) return "runtime_error";
  if (t.includes("compilation error")) return "compilation_error";
  if (t.includes("compile error")) return "compilation_error";
  if (t.includes("output match")) return "accepted";
  if (t.includes("expected")) return "wrong_answer";
  return null;
}

// ── Get verdict config ────────────────────────────────────
function getVerdictConfig(verdict) {
  const config = {
    accepted: {
      color: "#22c55e",
      bg: "rgba(34,197,94,0.1)",
      border: "rgba(34,197,94,0.3)",
      icon: "✅",
      label: "Accepted",
      showTips: false,
    },
    wrong_answer: {
      color: "#ef4444",
      bg: "rgba(239,68,68,0.1)",
      border: "rgba(239,68,68,0.3)",
      icon: "❌",
      label: "Wrong Answer",
      showTips: true,
    },
    time_limit_exceeded: {
      color: "#f97316",
      bg: "rgba(249,115,22,0.1)",
      border: "rgba(249,115,22,0.3)",
      icon: "⏱️",
      label: "Time Limit Exceeded",
      showTips: true,
    },
    memory_limit_exceeded: {
      color: "#a855f7",
      bg: "rgba(168,85,247,0.1)",
      border: "rgba(168,85,247,0.3)",
      icon: "💾",
      label: "Memory Limit Exceeded",
      showTips: true,
    },
    runtime_error: {
      color: "#f59e0b",
      bg: "rgba(245,158,11,0.1)",
      border: "rgba(245,158,11,0.3)",
      icon: "💥",
      label: "Runtime Error",
      showTips: true,
    },
    compilation_error: {
      color: "#6366f1",
      bg: "rgba(99,102,241,0.1)",
      border: "rgba(99,102,241,0.3)",
      icon: "🔧",
      label: "Compilation Error",
      showTips: true,
    },
  };
  return config[verdict] || config["wrong_answer"];
}

// ── Render verdict in sidebar ─────────────────────────────
async function renderVerdict(verdict) {
  const verdictArea = document.getElementById("cc-verdict-area");
  if (!verdictArea) return;

  const c = getVerdictConfig(verdict);
  const code = getCodeFromEditor();
  const language = getLanguage();
  const problemName = getProblemName();

  verdictArea.innerHTML = `
    <div style="
      background: ${c.bg};
      border: 2px solid ${c.border};
      border-radius: 12px;
      padding: 18px;
      margin-bottom: 14px;
      text-align: center;
    ">
      <div style="font-size:32px; margin-bottom:6px;">${c.icon}</div>
      <div style="font-size:22px; font-weight:800; color:${c.color}; margin-bottom:4px;">
        ${c.label}
      </div>
      <div style="color:#94a3b8; font-size:12px; margin-bottom: ${c.showTips ? "14px" : "0"};">
        ${c.showTips ? "Your solution failed. See tips below to fix it." : "Your solution passed all test cases! 🎉"}
      </div>
      ${c.showTips
      ? `<div style="text-align:left; border-top: 1px solid ${c.border}; padding-top:12px;">
               <div class="cc-section-title" style="margin-bottom:8px;">💡 Tips to Fix</div>
               <div id="cc-fix-tips">
                 <div style="color:#94a3b8; font-size:12px; padding:6px 0;">⏳ Getting tips...</div>
               </div>
             </div>`
      : ""
    }
    </div>
  `;

  if (sidebar) sidebar.classList.add("open");

  // Scroll verdict into view
  verdictArea.scrollIntoView({ behavior: "smooth", block: "start" });

  if (c.showTips) {
    try {
      const res = await fetch(`${API}/analyze-verdict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code,
          language,
          problem_name: problemName,
          verdict,
        }),
      });
      const data = await res.json();
      const tipsEl = document.getElementById("cc-fix-tips");
      if (tipsEl && data.verdict_tips) {
        tipsEl.innerHTML = data.verdict_tips
          .map(
            (tip, i) => `
            <div class="cc-tip">
              <span class="cc-tip-num">${i + 1}.</span>
              <span class="cc-tip-text">${tip}</span>
            </div>`,
          )
          .join("");
      }
    } catch (err) {
      const tipsEl = document.getElementById("cc-fix-tips");
      if (tipsEl)
        tipsEl.innerHTML = `<p style="color:#ef4444; font-size:12px;">Could not fetch tips.</p>`;
    }
  }
}

// ── Watch for Run / Submit result ─────────────────────────
function watchForResult() {
  let lastText = "";

  // Reset text tracking state if the user clicks any run or submit button,
  // allowing the exact same outcome ("Accepted") to be picked up again
  // and reopening the sidebar.
  document.body.addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (btn) {
      const text = btn.textContent.toLowerCase();
      const e2e = btn.getAttribute("data-e2e-locator") || "";
      if (text.includes("run") || text.includes("submit") || e2e.includes("run") || e2e.includes("submit")) {
        lastText = "";
      }
    }
  });

  const observer = new MutationObserver(() => {
    const verdict = scanPageForVerdict();
    if (verdict) {
      // Build a fingerprint from current page text to avoid re-triggering on same state
      const pageSnippet = document.body.innerText.slice(0, 1000);
      if (pageSnippet === lastText) return;
      lastText = pageSnippet;

      console.log("Coding Coach verdict detected:", verdict);

      // Re-open sidebar and render
      if (document.getElementById("cc-verdict-area")) {
        renderVerdict(verdict);
      } else {
        analyzeCode().then(() => {
          setTimeout(() => renderVerdict(verdict), 500);
        });
      }
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
  });
}

// ── Init ──────────────────────────────────────────────────
waitForEditor(() => {
  setTimeout(injectButton, 2000);
  watchForResult();
});

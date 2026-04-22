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

  // ── Detect language from actual editor code content ───────
  const code = (getCodeFromEditor() || "").toLowerCase();
  if (
    code.includes("class solution") ||
    code.includes("public int ") ||
    code.includes("public boolean ") ||
    code.includes("public string ") ||
    code.includes("public long ") ||
    code.includes("public list<") ||
    code.includes("public void ") ||
    code.includes("arraylist") ||
    code.includes("hashmap") ||
    code.includes("linkedlist") ||
    code.includes("new int[") ||
    code.includes("int[] ") ||
    code.includes("system.out")
  ) return "java";

  if (
    code.includes("#include") ||
    code.includes("vector<") ||
    code.includes("unordered_map") ||
    code.includes("cout <<") ||
    code.includes("nullptr") ||
    code.includes("std::")
  ) return "cpp";

  if (
    code.includes("console.log") ||
    code.includes("var ") ||
    code.includes("const ") ||
    code.includes("let ") ||
    code.includes("function ") ||
    code.includes("===")
  ) return "javascript";

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
      <h2>
        <div id="cc-header-logo">⚡</div>
        Coding Coach
      </h2>
      <button id="cc-close">✕</button>
    </div>
    <div id="cc-content">
      <div class="cc-loading">
        <div class="cc-loading-spinner"></div>
        <div style="font-size:13px;">Analyzing your code…</div>
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
    <div class="cc-loading-spinner"></div>
    <div style="font-size:13px;">Analyzing your code…</div>
    <div style="color:#1e293b; font-size:11px;">
      First load may take ~30 seconds
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

  // Similar Questions and Daily Challenge HTML
  let dailyHTML = "";
  if (data.daily_challenge && data.daily_challenge.title) {
    dailyHTML = `
      <div class="cc-section" style="margin-bottom:12px;">
        <div class="cc-section-title">🔥 Daily Challenge</div>
        <a href="https://leetcode.com${data.daily_challenge.link}" target="_blank" class="cc-daily-card">
          <div class="cc-daily-title">${data.daily_challenge.title}</div>
          <div class="cc-daily-meta">
            <span class="cc-daily-diff">${data.daily_challenge.difficulty}</span>
            <span class="cc-daily-date">${data.daily_challenge.date}</span>
          </div>
        </a>
      </div>
    `;
  }

  let similarHTML = "";
  if (data.similar_questions && data.similar_questions.length > 0) {
    const simList = data.similar_questions.map(q => `
      <a href="https://leetcode.com/problems/${q.slug}/" target="_blank" class="cc-sim-card">
        <div class="cc-sim-title">${q.title}</div>
        <div class="cc-sim-meta">
          <span class="cc-sim-diff">${q.difficulty}</span>
          <span style="color:#64748b; font-size:14px;">↗</span>
        </div>
      </a>
    `).join("");
    similarHTML = `
      <div class="cc-section">
        <div class="cc-section-title">🎯 Similar Questions</div>
        ${simList}
      </div>
    `;
  }

  document.getElementById("cc-content").innerHTML = `
    <div id="cc-save-area">
      <button class="cc-save-btn" id="cc-save-btn">💾 Save to History</button>
      <button id="cc-precheck-btn" style="
        width:100%;
        margin-top:8px;
        background: rgba(34,197,94,0.07);
        border: 1px solid rgba(34,197,94,0.25);
        color: #4ade80;
        font-size:12px;
        font-weight:600;
        padding:9px;
        border-radius:10px;
        cursor:pointer;
        font-family: 'Inter', -apple-system, sans-serif;
        letter-spacing: 0.01em;
        transition: all 0.2s;
      ">🔮 Pre-Check (AI Prediction)</button>
    </div>

    <div id="cc-precheck-area"></div>
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
    
    ${dailyHTML}
    ${similarHTML}
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

  // ── Pre-Check button listener ─────────────────────────────
  document.getElementById("cc-precheck-btn").addEventListener("click", async () => {
    // Clear any previous LeetCode execution results to avoid confusion
    const verdictArea = document.getElementById("cc-verdict-area");
    if (verdictArea) verdictArea.innerHTML = "";

    const preCheckArea = document.getElementById("cc-precheck-area");
    const preCheckBtn = document.getElementById("cc-precheck-btn");

    preCheckArea.innerHTML = `
      <div style="
        background: rgba(34,197,94,0.05);
        border: 1px solid rgba(34,197,94,0.2);
        border-radius:10px;
        padding:12px;
        margin-bottom:12px;
        text-align:center;
        color:#94a3b8;
        font-size:12px;
      ">⏳ AI is analyzing your code...</div>`;

    preCheckBtn.disabled = true;
    preCheckBtn.textContent = "🔮 Analyzing...";

    // Fetch fresh code directly right now so we don't use stale closure variables
    const freshCode = getCodeFromEditor();
    const freshLanguage = getLanguage();
    
    try {
      const res = await fetch(`${API}/pre-check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: freshCode, language: freshLanguage, problem_name: problemName }),
      });
      const data = await res.json();

      const predictionConfig = {
        likely_correct: { icon: "✅", color: "#22c55e", bg: "rgba(34,197,94,0.1)",  border: "rgba(34,197,94,0.3)",  label: "Likely Correct" },
        likely_wrong:   { icon: "❌", color: "#ef4444", bg: "rgba(239,68,68,0.1)",   border: "rgba(239,68,68,0.3)",   label: "Likely Wrong Answer" },
        likely_tle:     { icon: "⏱️", color: "#f97316", bg: "rgba(249,115,22,0.1)",  border: "rgba(249,115,22,0.3)",  label: "Likely TLE" },
        likely_error:   { icon: "💥", color: "#a855f7", bg: "rgba(168,85,247,0.1)",  border: "rgba(168,85,247,0.3)",  label: "Likely Error" },
        likely_compilation_error: { icon: "🔧", color: "#6366f1", bg: "rgba(99,102,241,0.1)", border: "rgba(99,102,241,0.3)", label: "Likely Compilation Error" },
      };

      const cfg = predictionConfig[data.prediction] || predictionConfig["likely_wrong"];
      const issuesHTML = (data.issues || []).length > 0
        ? `<div style="text-align:left; margin-top:10px; border-top: 1px solid ${cfg.border}; padding-top:10px;">
             <div style="font-size:11px; color:#94a3b8; margin-bottom:6px;">⚠️ Potential Issues:</div>
             ${data.issues.map(issue => `<div style="font-size:12px; color:#cbd5e1; padding:3px 0;">• ${issue}</div>`).join("")}
           </div>`
        : "";

      const confidenceBadge = {
        high:   { bg: "#166534", color: "#4ade80", text: "High Confidence" },
        medium: { bg: "#78350f", color: "#fbbf24", text: "Medium Confidence" },
        low:    { bg: "#1e1b4b", color: "#a5b4fc", text: "Low Confidence" },
      }[data.confidence] || { bg: "#1e1b4b", color: "#a5b4fc", text: "Low Confidence" };

      preCheckArea.innerHTML = `
        <div style="
          background: ${cfg.bg};
          border: 2px solid ${cfg.border};
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 14px;
          text-align: center;
        ">
          <div style="font-size:28px; margin-bottom:4px;">${cfg.icon}</div>
          <div style="font-size:18px; font-weight:800; color:${cfg.color}; margin-bottom:4px;">${cfg.label}</div>
          <span style="
            background: ${confidenceBadge.bg};
            color: ${confidenceBadge.color};
            font-size:10px;
            font-weight:600;
            padding:2px 8px;
            border-radius:20px;
            display:inline-block;
            margin-bottom:10px;
          ">${confidenceBadge.text}</span>
          <div style="font-size:12px; color:#cbd5e1; text-align:left;">${data.summary}</div>
          ${issuesHTML}
        </div>`;

    } catch (err) {
      preCheckArea.innerHTML = `<div style="color:#ef4444; font-size:12px; padding:8px;">❌ Pre-check failed. Make sure backend is running.</div>`;
    } finally {
      preCheckBtn.disabled = false;
      preCheckBtn.textContent = "🔮 Pre-Check (AI Prediction)";
    }
  });

  // Auto-check for an existing result output on the screen immediately
  // after rendering the sidebar, so if there is a verdict available it appears right away
  setTimeout(() => {
    const verdict = scanPageForVerdict();
    if (verdict) {
      renderVerdict(verdict);
    }
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

  // Clear any existing pre-check predictions to avoid confusion
  const preCheckArea = document.getElementById("cc-precheck-area");
  if (preCheckArea) preCheckArea.innerHTML = "";

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

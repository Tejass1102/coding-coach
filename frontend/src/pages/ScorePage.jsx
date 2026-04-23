import { useState, useEffect } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

// ── Colour helpers ─────────────────────────────────────────────────────────────
const levelMeta = {
  Newcomer:     { colour: "#94a3b8", bg: "rgba(148,163,184,.12)", emoji: "🌱" },
  Beginner:     { colour: "#60a5fa", bg: "rgba(96,165,250,.12)",  emoji: "📘" },
  Intermediate: { colour: "#facc15", bg: "rgba(250,204,21,.12)",  emoji: "⚡" },
  Advanced:     { colour: "#4ade80", bg: "rgba(74,222,128,.12)",  emoji: "🏆" },
  "No Data":    { colour: "#94a3b8", bg: "rgba(148,163,184,.08)", emoji: "❓" },
};

const scoreGradient = (s) =>
  s >= 80 ? ["#4ade80", "#22c55e"]
  : s >= 50 ? ["#facc15", "#f59e0b"]
  : s >= 20 ? ["#60a5fa", "#3b82f6"]
  : ["#94a3b8", "#64748b"];

// Heat colour for category bars: 0→grey, 0.33→blue, 0.67→amber, 1.0→green
const heatColour = (v) => {
  if (v >= 0.85) return "#4ade80";
  if (v >= 0.6)  return "#86efac";
  if (v >= 0.4)  return "#facc15";
  if (v >= 0.2)  return "#60a5fa";
  if (v > 0)     return "#818cf8";
  return "#334155";
};

const componentIcon = {
  time_decayed_quality:    "⏱️",
  consistency_frequency:   "📅",
  category_heatmap:        "🗺️",
  volume_tier:             "📦",
  optimization_complexity: "⚙️",
};

const componentLabel = {
  time_decayed_quality:    "Time-Decayed Quality",
  consistency_frequency:   "Consistency Frequency",
  category_heatmap:        "Category Heatmap",
  volume_tier:             "Volume Tier",
  optimization_complexity: "Optimization & Complexity",
};

const approachColour = {
  "Brute Force":         "rgba(239,68,68,.15)",
  "Sliding Window":      "rgba(96,165,250,.15)",
  "Dynamic Programming": "rgba(167,139,250,.15)",
  "Greedy":              "rgba(250,204,21,.15)",
  "Binary Search":       "rgba(52,211,153,.15)",
  "Divide & Conquer":    "rgba(251,146,60,.15)",
  "Hash Map":            "rgba(34,211,238,.15)",
  "Two Pointers":        "rgba(244,114,182,.15)",
};
const approachText = {
  "Brute Force":         "#f87171",
  "Sliding Window":      "#93c5fd",
  "Dynamic Programming": "#c4b5fd",
  "Greedy":              "#fde68a",
  "Binary Search":       "#6ee7b7",
  "Divide & Conquer":    "#fdba74",
  "Hash Map":            "#67e8f9",
  "Two Pointers":        "#f9a8d4",
};

function getProblemUrl(slug) {
  return `https://leetcode.com/problems/${slug}/`;
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function ScoreRing({ score }) {
  const [grad1, grad2] = scoreGradient(score);
  // SVG arc for donut ring
  const r = 70, cx = 90, cy = 90;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - score / 100);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <svg width="180" height="180" style={{ transform: "rotate(-90deg)" }}>
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={grad1} />
            <stop offset="100%" stopColor={grad2} />
          </linearGradient>
        </defs>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="14" />
        <circle
          cx={cx} cy={cy} r={r}
          fill="none"
          stroke="url(#ringGrad)"
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1)" }}
        />
      </svg>
      <div style={{
        marginTop: "-130px",
        fontSize: "42px",
        fontWeight: 800,
        background: `linear-gradient(135deg, ${grad1}, ${grad2})`,
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
        lineHeight: 1,
      }}>
        {score}
      </div>
      <div style={{ marginTop: "2px", color: "#cbd5e1", fontSize: "13px", marginBottom: "90px" }}>
        out of 100
      </div>
    </div>
  );
}

function DailyChallengeCard({ dailyChallenge }) {
  if (!dailyChallenge) return null;
  return (
    <div style={{
      background: "linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1))",
      border: "1px solid rgba(168, 85, 247, 0.2)",
      borderRadius: "16px",
      padding: "24px",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h2 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "16px", margin: 0 }}>
          🔥 Daily LeetCode Challenge
        </h2>
        <span style={{ color: "#a855f7", fontSize: "12px", fontWeight: 600 }}>{dailyChallenge.date}</span>
      </div>
      
      <a href={`https://leetcode.com${dailyChallenge.link}`} target="_blank" rel="noreferrer" style={{ textDecoration: "none" }}>
        <div style={{
          background: "rgba(255,255,255,.05)",
          border: "1px solid rgba(255,255,255,.1)",
          borderRadius: "12px", padding: "16px",
          display: "flex", justifyContent: "space-between", alignItems: "center",
          transition: "all 0.2s"
        }}
        onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,.1)"; }}
        onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,.05)"; }}>
          <div>
            <div style={{ color: "#f1f5f9", fontWeight: 600, fontSize: "15px", marginBottom: "4px" }}>
              {dailyChallenge.title}
            </div>
            <div style={{
              display: "inline-block", padding: "2px 8px", borderRadius: "4px", fontSize: "10px", fontWeight: 600,
              background: "rgba(255,255,255,.08)", color: "#cbd5e1"
            }}>
              {dailyChallenge.difficulty}
            </div>
          </div>
          <div style={{ fontSize: "20px" }}>↗</div>
        </div>
      </a>
    </div>
  );
}

function RecommendationsCard({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null;
  return (
    <div style={{
      background: "rgba(255,255,255,.08)",
      border: "1px solid rgba(255,255,255,.14)",
      borderRadius: "16px",
      padding: "24px",
    }}>
      <h2 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "16px", marginBottom: "16px" }}>
        🎯 Recommended Next Challenges
      </h2>
      <p style={{ color: "#94a3b8", fontSize: "13px", marginBottom: "20px" }}>
        Targeted to improve your weak areas:
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {recommendations.map((rec) => (
          <a key={rec.slug} href={getProblemUrl(rec.slug)} target="_blank" rel="noreferrer" style={{ textDecoration: "none" }}>
            <div style={{
              background: "rgba(255,255,255,.05)",
              border: "1px solid rgba(255,255,255,.08)",
              borderRadius: "10px", padding: "14px",
              display: "flex", justifyContent: "space-between", alignItems: "center",
              transition: "all 0.2s"
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255,255,255,.18)"; e.currentTarget.style.background = "rgba(255,255,255,.08)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255,255,255,.08)"; e.currentTarget.style.background = "rgba(255,255,255,.05)"; }}>
              <div>
                <div style={{ color: "#f1f5f9", fontWeight: 600, fontSize: "14px", marginBottom: "6px" }}>
                  {rec.title}
                </div>
                <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                  <span style={{ color: "#94a3b8", fontSize: "11px", fontWeight: 600 }}>{rec.difficulty}</span>
                  <span style={{ color: "#475569", fontSize: "10px" }}>•</span>
                  <span style={{ color: approachText[rec.approach] || "#94a3b8", fontSize: "11px", fontWeight: 500 }}>
                    {rec.approach}
                  </span>
                </div>
              </div>
              <div style={{ color: "#64748b" }}>↗</div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

function BreakdownBar({ label, icon, score, max, detail, colour }) {
  const pct = max > 0 ? (score / max) * 100 : 0;
  return (
    <div style={{ marginBottom: "18px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
        <span style={{ color: "#cbd5e1", fontSize: "14px" }}>
          {icon} {label}
        </span>
        <span style={{ fontWeight: 700, fontSize: "14px", color: colour }}>
          {score} <span style={{ color: "#94a3b8", fontWeight: 400 }}>/ {max}</span>
        </span>
      </div>
      <div style={{
        width: "100%", height: "8px", borderRadius: "99px",
        background: "rgba(255,255,255,.06)", overflow: "hidden",
      }}>
        <div style={{
          width: `${pct}%`, height: "100%", borderRadius: "99px",
          background: colour,
          transition: "width 1s cubic-bezier(.4,0,.2,1)",
        }} />
      </div>
      <p style={{ color: "#94a3b8", fontSize: "11px", marginTop: "4px" }}>{detail}</p>
    </div>
  );
}

function CategoryHeatmap({ heatmap }) {
  if (!heatmap || Object.keys(heatmap).length === 0) return null;

  const categoryIcon = {
    "Arrays/Strings":      "📋",
    "Trees/Graphs":        "🌳",
    "Dynamic Programming": "🧮",
    "Linked Lists":        "🔗",
    "Math/Search":         "🔍",
  };

  return (
    <div style={{
      background: "rgba(255,255,255,.08)",
      border: "1px solid rgba(255,255,255,.14)",
      borderRadius: "16px",
      padding: "24px",
    }}>
      <h2 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "16px", marginBottom: "20px" }}>
        🗺️ Category Heatmap
      </h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "12px" }}>
        {Object.entries(heatmap).map(([cat, val]) => {
          const colour = heatColour(val);
          const pct = Math.round(val * 100);
          return (
            <div key={cat} style={{
              background: `${colour}18`,
              border: `1px solid ${colour}40`,
              borderRadius: "12px",
              padding: "16px 14px",
              textAlign: "center",
              position: "relative",
              overflow: "hidden",
            }}>
              {/* background fill bar */}
              <div style={{
                position: "absolute", bottom: 0, left: 0,
                width: "100%", height: `${pct}%`,
                background: `${colour}0d`,
                transition: "height 1.2s ease",
              }} />
              <div style={{ fontSize: "22px", marginBottom: "6px" }}>
                {categoryIcon[cat] || "📌"}
              </div>
              <div style={{ color: "#f1f5f9", fontSize: "12px", fontWeight: 600, marginBottom: "8px", lineHeight: 1.3 }}>
                {cat}
              </div>
              <div style={{
                fontSize: "20px", fontWeight: 800, color: colour,
              }}>
                {pct}%
              </div>
              <div style={{ color: "#cbd5e1", fontSize: "10px", marginTop: "2px" }}>
                avg difficulty
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ApproachFrequency({ frequency, total }) {
  const sorted = Object.entries(frequency).sort((a, b) => b[1] - a[1]);
  if (sorted.length === 0) return null;
  const maxCount = sorted[0][1];

  return (
    <div style={{
      background: "rgba(255,255,255,.08)",
      border: "1px solid rgba(255,255,255,.14)",
      borderRadius: "16px",
      padding: "24px",
    }}>
      <h2 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "16px", marginBottom: "20px" }}>
        🎯 Approach Usage
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {sorted.map(([approach, count]) => (
          <div key={approach} style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{
              width: "170px", fontSize: "13px", flexShrink: 0,
              color: approachText[approach] || "#94a3b8",
            }}>
              {approach}
            </span>
            <div style={{
              flex: 1, height: "8px", borderRadius: "99px",
              background: "rgba(255,255,255,.06)", overflow: "hidden",
            }}>
              <div style={{
                width: `${(count / maxCount) * 100}%`,
                height: "100%", borderRadius: "99px",
                background: approachText[approach] || "#94a3b8",
                opacity: 0.7,
                transition: "width 1s ease",
              }} />
            </div>
            <span style={{ color: "#94a3b8", fontSize: "12px", width: "28px", textAlign: "right" }}>
              {count}×
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AreasGrid({ strongAreas, weakAreas }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
      {/* Strong */}
      <div style={{
        background: "rgba(255,255,255,.08)",
        border: "1px solid rgba(255,255,255,.14)",
        borderRadius: "16px", padding: "24px",
      }}>
        <h2 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "16px", marginBottom: "14px" }}>
          💪 Strong Areas
        </h2>
        {strongAreas.length === 0 ? (
          <p style={{ color: "#94a3b8", fontSize: "13px" }}>
            Solve non-brute-force problems to build strong areas.
          </p>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {strongAreas.map((a) => (
              <span key={a} style={{
                fontSize: "12px", padding: "4px 12px", borderRadius: "99px",
                background: approachColour[a] || "rgba(255,255,255,.08)",
                color: approachText[a] || "#94a3b8",
                border: `1px solid ${approachText[a] || "#94a3b8"}40`,
              }}>
                ✓ {a}
              </span>
            ))}
          </div>
        )}
      </div>
      {/* Weak */}
      <div style={{
        background: "rgba(255,255,255,.08)",
        border: "1px solid rgba(255,255,255,.14)",
        borderRadius: "16px", padding: "24px",
      }}>
        <h2 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "16px", marginBottom: "14px" }}>
          📈 Areas to Improve
        </h2>
        {weakAreas.length === 0 ? (
          <p style={{ color: "#4ade80", fontSize: "13px" }}>
            🎉 You have covered all approaches!
          </p>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {weakAreas.map((a) => (
              <span key={a} style={{
                fontSize: "12px", padding: "4px 12px", borderRadius: "99px",
                background: "rgba(255,255,255,.08)",
                color: "#94a3b8",
                border: "1px solid rgba(255,255,255,.13)",
              }}>
                ○ {a}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main page ──────────────────────────────────────────────────────────────────

function ScorePage() {
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);

  useEffect(() => { fetchScore(); }, []);

  const fetchScore = async () => {
    try {
      const res = await axios.get(`${API}/score`);
      setScoreData(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch score data.");
    } finally {
      setLoading(false);
    }
  };

  // ── Loading ──
  if (loading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "60vh", gap: "16px" }}>
        <div style={{
          width: "48px", height: "48px", borderRadius: "50%",
          border: "3px solid rgba(255,255,255,.08)",
          borderTopColor: "#60a5fa",
          animation: "spin 0.8s linear infinite",
        }} />
        <p style={{ color: "#94a3b8", fontSize: "14px" }}>Calculating your score…</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: "center", color: "#f87171", padding: "60px" }}>
        {error}
      </div>
    );
  }

  if (!scoreData) return null;

  const meta = levelMeta[scoreData.level] || levelMeta["Newcomer"];
  const [grad1, grad2] = scoreGradient(scoreData.score);

  // Build breakdown bar colours cycling through a palette
  const barColours = ["#60a5fa", "#a78bfa", "#34d399", "#fb923c", "#f472b6"];

  return (
    <div style={{
      maxWidth: "1200px", margin: "0 auto",
      padding: "40px 24px",
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
    }}>

      {/* ── Hero section ──────────────────────────────────────────────────── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "36px" }}>
        <div>
          <h1 style={{ color: "#f1f5f9", fontWeight: 800, fontSize: "28px", margin: "0 0 6px 0" }}>
            Interview Readiness Score
          </h1>
          <p style={{ color: "#94a3b8", fontSize: "14px", margin: 0 }}>
            Based on {scoreData.total_submissions} submission{scoreData.total_submissions !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => { setLoading(true); fetchScore(); }}
          style={{
            padding: "10px 24px", borderRadius: "8px",
            background: "rgba(96,165,250,.15)",
            border: "1px solid rgba(96,165,250,.3)",
            color: "#60a5fa", fontSize: "13px", fontWeight: 600,
            cursor: "pointer", transition: "all .2s",
          }}
          onMouseEnter={(e) => { e.target.style.background = "rgba(96,165,250,.25)"; }}
          onMouseLeave={(e) => { e.target.style.background = "rgba(96,165,250,.15)"; }}
        >
          ↻ Refresh Data
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: "24px", alignItems: "start" }}>
        
        {/* ── Left Column ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          
          {/* ── Score card ── */}
          <div style={{
            background: "rgba(255,255,255,.08)",
            border: "1px solid rgba(255,255,255,.14)",
            borderRadius: "20px", padding: "36px",
            display: "flex", flexDirection: "column", alignItems: "center",
            position: "relative", overflow: "hidden",
          }}>
            {/* subtle radial glow */}
            <div style={{
              position: "absolute", top: "-60px", left: "50%", transform: "translateX(-50%)",
              width: "300px", height: "300px", borderRadius: "50%",
              background: `radial-gradient(circle, ${grad1}22 0%, transparent 70%)`,
              pointerEvents: "none",
            }} />

            <ScoreRing score={scoreData.score} />

            {/* Level badge */}
            <div style={{
              display: "inline-flex", alignItems: "center", gap: "8px",
              padding: "8px 20px", borderRadius: "99px",
              background: meta.bg,
              border: `1px solid ${meta.colour}40`,
              color: meta.colour, fontWeight: 700, fontSize: "16px",
              marginBottom: "14px",
            }}>
              {meta.emoji} {scoreData.level}
            </div>

            <p style={{ color: "#cbd5e1", fontSize: "14px", maxWidth: "420px", textAlign: "center" }}>
              {scoreData.message}
            </p>
          </div>

          {/* ── Score Breakdown ── */}
          {Object.keys(scoreData.breakdown || {}).length > 0 && (
            <div style={{
              background: "rgba(255,255,255,.08)",
              border: "1px solid rgba(255,255,255,.14)",
              borderRadius: "16px", padding: "24px",
            }}>
              <h2 style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "16px", marginBottom: "20px" }}>
                📊 Score Breakdown
              </h2>
              {Object.entries(scoreData.breakdown).map(([key, data], i) => (
                <BreakdownBar
                  key={key}
                  label={componentLabel[key] || key.replace(/_/g, " ")}
                  icon={componentIcon[key] || "◆"}
                  score={data.score}
                  max={data.max}
                  detail={data.detail}
                  colour={barColours[i % barColours.length]}
                />
              ))}
            </div>
          )}

        </div>

        {/* ── Right Column ── */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          
          <DailyChallengeCard dailyChallenge={scoreData.daily_challenge} />
          
          <RecommendationsCard recommendations={scoreData.recommended_questions} />
          
          <CategoryHeatmap heatmap={scoreData.category_heatmap} />
          
          <AreasGrid
            strongAreas={scoreData.strong_areas || []}
            weakAreas={scoreData.weak_areas || []}
          />
          
          <ApproachFrequency
            frequency={scoreData.approach_frequency || {}}
            total={scoreData.total_submissions}
          />

        </div>

      </div>
    </div>
  );
}

export default ScorePage;

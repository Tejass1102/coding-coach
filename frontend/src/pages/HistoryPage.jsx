import { useState, useEffect } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const approachMeta = {
  "Brute Force":         { color: "#f87171", bg: "rgba(239,68,68,0.1)",   border: "rgba(239,68,68,0.25)" },
  "Sliding Window":      { color: "#60a5fa", bg: "rgba(96,165,250,0.1)",  border: "rgba(96,165,250,0.25)" },
  "Dynamic Programming": { color: "#c084fc", bg: "rgba(192,132,252,0.1)", border: "rgba(192,132,252,0.25)" },
  "Greedy":              { color: "#fbbf24", bg: "rgba(251,191,36,0.1)",  border: "rgba(251,191,36,0.25)" },
  "Binary Search":       { color: "#34d399", bg: "rgba(52,211,153,0.1)",  border: "rgba(52,211,153,0.25)" },
  "Divide & Conquer":    { color: "#fb923c", bg: "rgba(251,146,60,0.1)",  border: "rgba(251,146,60,0.25)" },
  "Hash Map":            { color: "#22d3ee", bg: "rgba(34,211,238,0.1)",  border: "rgba(34,211,238,0.25)" },
  "Two Pointers":        { color: "#f472b6", bg: "rgba(244,114,182,0.1)", border: "rgba(244,114,182,0.25)" },
};

const defaultMeta = { color: "#94a3b8", bg: "rgba(148,163,184,0.08)", border: "rgba(148,163,184,0.2)" };

function getProblemUrl(name) {
  let slug = name.replace(/^\d+\.\s*/, "");
  slug = slug.replace(/[^a-zA-Z0-9\s-]/g, "");
  return `https://leetcode.com/problems/${slug.trim().toLowerCase().replace(/\s+/g, "-")}/`;
}

function ApproachBadge({ approach }) {
  const m = approachMeta[approach] || defaultMeta;
  return (
    <span style={{
      fontSize: "11px", fontWeight: 600,
      padding: "3px 10px", borderRadius: "99px",
      background: m.bg, border: `1px solid ${m.border}`, color: m.color,
    }}>
      {approach}
    </span>
  );
}

function HistoryPage() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => { fetchHistory(); }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API}/history`);
      setSubmissions(res.data.submissions);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh", flexDirection: "column", gap: "16px" }}>
        <div style={{
          width: "40px", height: "40px", borderRadius: "50%",
          border: "2px solid rgba(99,102,241,0.2)",
          borderTopColor: "#6366f1",
          animation: "spin 0.8s linear infinite",
        }} />
        <p style={{ color: "#94a3b8", fontSize: "13px" }}>Loading history…</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: "1200px", margin: "0 auto",
      padding: "36px 24px",
      fontFamily: "'Inter', sans-serif",
    }}>
      {/* Header */}
      <div style={{ marginBottom: "28px" }}>
        <h1 style={{ color: "#f1f5f9", fontWeight: 800, fontSize: "26px", marginBottom: "6px", letterSpacing: "-0.03em" }}>
          Submission History
        </h1>
        <p style={{ color: "#475569", fontSize: "13px" }}>
          {submissions.length} problem{submissions.length !== 1 ? "s" : ""} solved
        </p>
      </div>

      {submissions.length === 0 ? (
        <div style={{
          textAlign: "center", padding: "80px 24px",
          background: "rgba(255,255,255,0.06)",
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: "16px",
          color: "#64748b",
        }}>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>📭</div>
          <p style={{ fontSize: "14px" }}>No submissions yet. Start solving problems!</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", alignItems: "start" }}>

          {/* ── Left list ── */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {submissions.map((sub, idx) => {
              const analysis = sub.analyses?.[0];
              const isActive = selected?.id === sub.id;
              return (
                <div
                  key={sub.id}
                  onClick={() => setSelected(sub)}
                  style={{
                    background: isActive ? "rgba(99,102,241,0.12)" : "rgba(255,255,255,0.06)",
                    border: `1px solid ${isActive ? "rgba(99,102,241,0.35)" : "rgba(255,255,255,0.12)"}`,
                    borderRadius: "12px",
                    padding: "14px 16px",
                    cursor: "pointer",
                    transition: "all 0.18s",
                    position: "relative",
                    overflow: "hidden",
                  }}
                  onMouseEnter={e => { if (!isActive) e.currentTarget.style.borderColor = "rgba(255,255,255,0.18)"; }}
                  onMouseLeave={e => { if (!isActive) e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"; }}
                >
                  {/* Subtle left accent when active */}
                  {isActive && (
                    <div style={{
                      position: "absolute", left: 0, top: 0, bottom: 0, width: "3px",
                      background: "linear-gradient(180deg, #6366f1, #06b6d4)",
                      borderRadius: "3px 0 0 3px",
                    }} />
                  )}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                    <span style={{ color: "#f1f5f9", fontWeight: 600, fontSize: "13px", paddingLeft: isActive ? "8px" : "0" }}>
                      {sub.problem_name}
                    </span>
                    <span style={{ color: "#94a3b8", fontSize: "11px", flexShrink: 0, marginLeft: "8px" }}>
                      {new Date(sub.submitted_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                    </span>
                  </div>
                  {analysis && (
                    <div style={{ paddingLeft: isActive ? "8px" : "0" }}>
                      <ApproachBadge approach={analysis.predicted_approach} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* ── Right detail panel ── */}
          <div style={{
            background: "rgba(255,255,255,0.07)",
            border: "1px solid rgba(255,255,255,0.13)",
            borderRadius: "16px",
            padding: "24px",
            position: "sticky",
            top: "80px",
          }}>
            {selected ? (() => {
              const a = selected.analyses?.[0];
              const m = approachMeta[a?.predicted_approach] || defaultMeta;
              return (
                <>
                  {/* Problem title link */}
                  <a
                    href={getProblemUrl(selected.problem_name)}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: "inline-flex", alignItems: "center", gap: "6px",
                      color: "#a5b4fc", fontWeight: 700, fontSize: "16px",
                      textDecoration: "none", marginBottom: "20px",
                      transition: "color 0.15s",
                    }}
                    onMouseEnter={e => e.currentTarget.style.color = "#c7d2fe"}
                    onMouseLeave={e => e.currentTarget.style.color = "#a5b4fc"}
                  >
                    {selected.problem_name}
                    <span style={{ fontSize: "12px", opacity: 0.6 }}>↗</span>
                  </a>

                  {a && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>

                      {/* Approach */}
                      <div style={{
                        background: m.bg, border: `1px solid ${m.border}`,
                        borderRadius: "10px", padding: "14px",
                      }}>
                        <p style={{ color: "#94a3b8", fontSize: "10px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px" }}>
                          Approach
                        </p>
                        <p style={{ color: m.color, fontWeight: 700, fontSize: "18px" }}>
                          {a.predicted_approach}
                        </p>
                      </div>

                      {/* Complexity row */}
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                        {[
                          { label: "Time", value: a.time_complexity },
                          { label: "Space", value: a.space_complexity },
                        ].map(({ label, value }) => (
                          <div key={label} style={{
                            background: "rgba(255,255,255,0.07)",
                            border: "1px solid rgba(255,255,255,0.13)",
                            borderRadius: "10px", padding: "12px",
                          }}>
                            <p style={{ color: "#94a3b8", fontSize: "10px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "4px" }}>
                              {label}
                            </p>
                            <p style={{ color: "#cbd5e1", fontSize: "12px", lineHeight: 1.5 }}>{value}</p>
                          </div>
                        ))}
                      </div>

                      {/* Difficulty */}
                      <div>
                        <p style={{ color: "#94a3b8", fontSize: "10px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "8px" }}>
                          Difficulty
                        </p>
                        <p style={{ color: "#cbd5e1", fontSize: "13px" }}>{a.difficulty_level}</p>
                      </div>

                      {/* Optimization Tips */}
                      <div>
                        <p style={{ color: "#94a3b8", fontSize: "10px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px" }}>
                          Optimization Tips
                        </p>
                        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                          {(a.optimization_tips || []).map((tip, i) => (
                            <div key={i} style={{
                              display: "flex", gap: "10px",
                              background: "rgba(99,102,241,0.06)",
                              border: "1px solid rgba(99,102,241,0.15)",
                              borderRadius: "8px", padding: "10px 12px",
                            }}>
                              <span style={{ color: "#6366f1", fontWeight: 700, fontSize: "11px", flexShrink: 0 }}>
                                {i + 1}.
                              </span>
                              <p style={{ color: "#cbd5e1", fontSize: "12px", lineHeight: 1.6 }}>{tip}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </>
              );
            })() : (
              <div style={{ textAlign: "center", padding: "48px 0", color: "#64748b" }}>
                <div style={{ fontSize: "36px", marginBottom: "12px" }}>👈</div>
                <p style={{ fontSize: "13px" }}>Select a submission to see details</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default HistoryPage;

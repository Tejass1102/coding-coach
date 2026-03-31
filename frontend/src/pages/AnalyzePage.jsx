import { useState, useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";
import axios from "axios";

const API = "http://127.0.0.1:8000/api";
const DEBOUNCE_DELAY = 3000; // 3 seconds

function AnalyzePage() {
  const [code, setCode] = useState("# Write your code here\n");
  const [language, setLanguage] = useState("python");
  const [problemName, setProblemName] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const debounceTimer = useRef(null);
  const countdownTimer = useRef(null);

  // ── Auto analyze with debounce ──────────────────────
  useEffect(() => {
    if (!code.trim() || code.trim() === "# Write your code here") {
      setCountdown(null);
      return;
    }

    setSaved(false);

    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    if (countdownTimer.current) clearInterval(countdownTimer.current);

    setCountdown(3);
    let count = 3;
    countdownTimer.current = setInterval(() => {
      count -= 1;
      setCountdown(count);
      if (count <= 0) {
        clearInterval(countdownTimer.current);
        setCountdown(null);
      }
    }, 1000);

    debounceTimer.current = setTimeout(() => {
      handleAutoAnalyze();
    }, DEBOUNCE_DELAY);

    return () => {
      clearTimeout(debounceTimer.current);
      clearInterval(countdownTimer.current);
    };
  }, [code, language]);

  const handleAutoAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API}/analyze-only`, {
        code,
        language,
        problem_name: problemName || "Unknown Problem",
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong!");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!result) return;
    setSaving(true);
    setError(null);
    try {
      const response = await axios.post(`${API}/save-submission`, {
        code,
        language,
        problem_name: problemName || "Unknown Problem",
      });
      setResult(response.data);
      setSaved(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save!");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold text-white mb-2">Analyze Your Code</h1>
      <p className="text-slate-400 mb-8">
        Write your code and get instant AI-powered feedback automatically
      </p>

      {/* Input Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Left — Editor */}
        <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Problem name (e.g. Two Sum)"
                value={problemName}
                onChange={(e) => setProblemName(e.target.value)}
                className="bg-slate-700 text-white text-sm px-3 py-1.5 rounded-lg border border-slate-600 focus:outline-none focus:border-blue-500 w-48"
              />
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-slate-700 text-white text-sm px-3 py-1.5 rounded-lg border border-slate-600 focus:outline-none"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              {countdown !== null && (
                <span className="text-yellow-400 text-xs flex items-center gap-1">
                  ⏳ Analyzing in {countdown}s
                </span>
              )}
              {loading && (
                <span className="text-blue-400 text-xs flex items-center gap-1">
                  🔄 Analyzing...
                </span>
              )}
              {!loading && !countdown && result && (
                <span className="text-green-400 text-xs flex items-center gap-1">
                  ✅ Analysis ready
                </span>
              )}
            </div>
          </div>

          <Editor
            height="400px"
            language={language === "cpp" ? "cpp" : language}
            value={code}
            onChange={(value) => setCode(value || "")}
            theme="vs-dark"
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              padding: { top: 16 },
            }}
          />
        </div>

        {/* Right — How it works + Save button */}
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white mb-4">
              How it works
            </h2>
            <div className="space-y-4">
              {[
                {
                  icon: "🧬",
                  title: "Auto Analysis",
                  desc: "Code is automatically analyzed 3 seconds after you stop typing — no need to click anything",
                },
                {
                  icon: "🎯",
                  title: "Approach Detection",
                  desc: "Our trained DL classifier detects which algorithm pattern you used",
                },
                {
                  icon: "💡",
                  title: "AI Feedback",
                  desc: "Groq LLM generates detailed tips, complexity analysis and optimization suggestions",
                },
                {
                  icon: "💾",
                  title: "Save to History",
                  desc: "Click Save when you are happy with your solution to track your progress and update your score",
                },
              ].map((item, i) => (
                <div key={i} className="flex gap-3">
                  <span className="text-2xl">{item.icon}</span>
                  <div>
                    <p className="text-white font-medium text-sm">
                      {item.title}
                    </p>
                    <p className="text-slate-400 text-xs">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Save Button */}
          <div className="mt-6 space-y-3">
            {saved && (
              <div className="bg-green-900/30 border border-green-500 text-green-400 px-4 py-2 rounded-xl text-sm text-center">
                ✅ Saved to history and score updated!
              </div>
            )}
            <button
              onClick={handleSave}
              disabled={!result || saving || saved}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-700 disabled:cursor-not-allowed disabled:text-slate-500 text-white font-semibold py-3 rounded-xl transition-all text-lg"
            >
              {saving
                ? "💾 Saving..."
                : saved
                  ? "✅ Saved!"
                  : "💾 Save Submission"}
            </button>
            <p className="text-slate-500 text-xs text-center">
              Analysis is automatic — Save only when ready to track progress
            </p>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/30 border border-red-500 text-red-400 px-4 py-3 rounded-xl mb-6">
          ❌ {error}
        </div>
      )}

      {/* Loading skeleton */}
      {loading && !result && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-slate-800 rounded-xl border border-slate-700 p-6 animate-pulse"
            >
              <div className="h-4 bg-slate-700 rounded w-1/4 mb-4"></div>
              <div className="h-3 bg-slate-700 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-slate-700 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* ── Approach Detection — clean, name only ── */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-white">
                🎯 Approach Detected
              </h2>
              {loading && (
                <span className="text-blue-400 text-xs">🔄 Updating...</span>
              )}
            </div>
            <span className="text-3xl font-bold text-blue-400">
              {result.analysis.final_approach || result.approach_detection.predicted_approach}
            </span>
          </div>

          {/* Analysis Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
              <h2 className="text-lg font-semibold text-white mb-4">
                ⏱️ Complexity Analysis
              </h2>
              <div className="space-y-3">
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-xs text-slate-400 mb-1">Time Complexity</p>
                  <p className="text-white text-sm">
                    {result.analysis.time_complexity}
                  </p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-xs text-slate-400 mb-1">
                    Space Complexity
                  </p>
                  <p className="text-white text-sm">
                    {result.analysis.space_complexity}
                  </p>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-xs text-slate-400 mb-1">
                    Difficulty Level
                  </p>
                  <p className="text-white text-sm">
                    {result.analysis.difficulty_level}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
              <h2 className="text-lg font-semibold text-white mb-4">
                ✅ Good Practices
              </h2>
              <div className="space-y-2">
                {result.analysis.good_practices.map((tip, i) => (
                  <div
                    key={i}
                    className="flex gap-2 bg-green-900/20 border border-green-800/30 rounded-lg p-3"
                  >
                    <span className="text-green-400 text-sm">✓</span>
                    <p className="text-slate-300 text-sm">{tip}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-3">
              🧠 Approach Explanation
            </h2>
            <p className="text-slate-300 leading-relaxed">
              {result.analysis.approach_explanation}
            </p>
          </div>

          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              🚀 Optimization Tips
            </h2>
            <div className="space-y-3">
              {result.analysis.optimization_tips.map((tip, i) => (
                <div
                  key={i}
                  className="flex gap-3 bg-blue-900/20 border border-blue-800/30 rounded-lg p-4"
                >
                  <span className="text-blue-400 font-bold text-sm min-w-6">
                    {i + 1}.
                  </span>
                  <p className="text-slate-300 text-sm">{tip}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyzePage;

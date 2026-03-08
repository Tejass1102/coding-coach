import { useState } from "react";
import Editor from "@monaco-editor/react";
import axios from "axios";

const API = "http://127.0.0.1:8000/api";

function AnalyzePage() {
  const [code, setCode] = useState("# Write your code here\n");
  const [language, setLanguage] = useState("python");
  const [problemName, setProblemName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!code.trim() || code.trim() === "# Write your code here") {
      setError("Please write some code first!");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await axios.post(`${API}/analyze`, {
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

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return "text-green-400";
    if (confidence >= 50) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold text-white mb-2">Analyze Your Code</h1>
      <p className="text-slate-400 mb-8">
        Paste your solution and get instant AI-powered feedback
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

        {/* Right — Quick Stats or Placeholder */}
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white mb-4">
              How it works
            </h2>
            <div className="space-y-4">
              {[
                {
                  icon: "🧬",
                  title: "CodeBERT Analysis",
                  desc: "Your code is converted to a 768-dim embedding vector using Microsoft's CodeBERT model",
                },
                {
                  icon: "🎯",
                  title: "Approach Detection",
                  desc: "Our trained classifier detects which algorithm pattern you used with confidence score",
                },
                {
                  icon: "💡",
                  title: "AI Feedback",
                  desc: "Groq LLM generates detailed tips, complexity analysis and optimization suggestions",
                },
                {
                  icon: "📊",
                  title: "Score Tracking",
                  desc: "Every submission updates your interview readiness score out of 100",
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
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-all text-lg"
          >
            {loading ? "⏳ Analyzing..." : "⚡ Analyze Code"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/30 border border-red-500 text-red-400 px-4 py-3 rounded-xl mb-6">
          ❌ {error}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Approach Detection */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              🎯 Approach Detection
            </h2>
            <div className="flex items-center gap-4 mb-4">
              <span className="text-3xl font-bold text-blue-400">
                {result.approach_detection.predicted_approach}
              </span>
              <span
                className={`text-2xl font-bold ${getConfidenceColor(result.approach_detection.confidence)}`}
              >
                {result.approach_detection.confidence}%
              </span>
              <span className="text-slate-400 text-sm">confidence</span>
            </div>

            {/* All scores bar chart */}
            <div className="space-y-2">
              {Object.entries(result.approach_detection.all_scores)
                .sort((a, b) => b[1] - a[1])
                .map(([approach, score]) => (
                  <div key={approach} className="flex items-center gap-3">
                    <span className="text-slate-400 text-xs w-36">
                      {approach}
                    </span>
                    <div className="flex-1 bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all"
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <span className="text-slate-300 text-xs w-12 text-right">
                      {score.toFixed(1)}%
                    </span>
                  </div>
                ))}
            </div>
          </div>

          {/* Analysis Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Complexity */}
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

            {/* Good Practices */}
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

          {/* Approach Explanation */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-white mb-3">
              🧠 Approach Explanation
            </h2>
            <p className="text-slate-300 leading-relaxed">
              {result.analysis.approach_explanation}
            </p>
          </div>

          {/* Optimization Tips */}
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

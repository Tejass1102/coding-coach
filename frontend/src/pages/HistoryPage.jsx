import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000/api";

function HistoryPage() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

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

  const getApproachColor = (approach) => {
    const colors = {
      "Brute Force": "bg-red-900/40 text-red-400 border-red-800",
      "Sliding Window": "bg-blue-900/40 text-blue-400 border-blue-800",
      "Dynamic Programming":
        "bg-purple-900/40 text-purple-400 border-purple-800",
      Greedy: "bg-yellow-900/40 text-yellow-400 border-yellow-800",
      "Binary Search": "bg-green-900/40 text-green-400 border-green-800",
      "Divide & Conquer": "bg-orange-900/40 text-orange-400 border-orange-800",
      "Hash Map": "bg-cyan-900/40 text-cyan-400 border-cyan-800",
      "Two Pointers": "bg-pink-900/40 text-pink-400 border-pink-800",
    };
    return colors[approach] || "bg-slate-700 text-slate-400 border-slate-600";
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-slate-400 text-center py-20">
          Loading history...
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold text-white mb-2">Submission History</h1>
      <p className="text-slate-400 mb-8">
        {submissions.length} total submissions
      </p>

      {submissions.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          No submissions yet. Go analyze some code!
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left — Submission List */}
          <div className="space-y-3">
            {submissions.map((sub) => {
              const analysis = sub.analyses?.[0];
              return (
                <div
                  key={sub.id}
                  onClick={() => setSelected(sub)}
                  className={`bg-slate-800 rounded-xl border p-4 cursor-pointer transition-all hover:border-blue-500 ${
                    selected?.id === sub.id
                      ? "border-blue-500"
                      : "border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-white font-semibold">
                      {sub.problem_name}
                    </h3>
                    <span className="text-slate-500 text-xs">
                      {new Date(sub.submitted_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <span className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded-full">
                      {sub.language}
                    </span>
                    {analysis && (
                      <span
                        className={`text-xs border px-2 py-1 rounded-full ${getApproachColor(analysis.predicted_approach)}`}
                      >
                        {analysis.predicted_approach}
                      </span>
                    )}
                    {analysis && (
                      <span className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded-full">
                        {analysis.confidence.toFixed(1)}% confidence
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right — Selected Detail */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 h-fit sticky top-6">
            {selected ? (
              <>
                <h2 className="text-xl font-bold text-white mb-4">
                  {selected.problem_name}
                </h2>
                {selected.analyses?.[0] && (
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Approach</p>
                      <span
                        className={`text-sm border px-3 py-1 rounded-full ${getApproachColor(selected.analyses[0].predicted_approach)}`}
                      >
                        {selected.analyses[0].predicted_approach}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">
                        Time Complexity
                      </p>
                      <p className="text-white text-sm">
                        {selected.analyses[0].time_complexity}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">
                        Space Complexity
                      </p>
                      <p className="text-white text-sm">
                        {selected.analyses[0].space_complexity}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-2">
                        Optimization Tips
                      </p>
                      <div className="space-y-2">
                        {selected.analyses[0].optimization_tips.map(
                          (tip, i) => (
                            <div
                              key={i}
                              className="flex gap-2 bg-blue-900/20 border border-blue-800/30 rounded-lg p-2"
                            >
                              <span className="text-blue-400 text-xs">
                                {i + 1}.
                              </span>
                              <p className="text-slate-300 text-xs">{tip}</p>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Difficulty</p>
                      <p className="text-white text-sm">
                        {selected.analyses[0].difficulty_level}
                      </p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-slate-400 text-center py-10">
                Click a submission to see details
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default HistoryPage;

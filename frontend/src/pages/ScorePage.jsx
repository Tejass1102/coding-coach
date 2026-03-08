import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000/api";

function ScorePage() {
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScore();
  }, []);

  const fetchScore = async () => {
    try {
      const res = await axios.get(`${API}/score`);
      setScoreData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (level) => {
    const colors = {
      Newcomer: "text-slate-400",
      Beginner: "text-blue-400",
      Intermediate: "text-yellow-400",
      Advanced: "text-green-400",
    };
    return colors[level] || "text-white";
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-green-400";
    if (score >= 50) return "text-yellow-400";
    if (score >= 20) return "text-blue-400";
    return "text-slate-400";
  };

  const getApproachColor = (approach) => {
    const colors = {
      "Brute Force": "bg-red-900/40 text-red-400",
      "Sliding Window": "bg-blue-900/40 text-blue-400",
      "Dynamic Programming": "bg-purple-900/40 text-purple-400",
      Greedy: "bg-yellow-900/40 text-yellow-400",
      "Binary Search": "bg-green-900/40 text-green-400",
      "Divide & Conquer": "bg-orange-900/40 text-orange-400",
    };
    return colors[approach] || "bg-slate-700 text-slate-400";
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="text-slate-400 text-center py-20">
          Calculating your score...
        </div>
      </div>
    );
  }

  if (!scoreData) return null;

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold text-white mb-2">
        Interview Readiness Score
      </h1>
      <p className="text-slate-400 mb-8">
        Based on {scoreData.total_submissions} submissions
      </p>

      {/* Main Score Card */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 mb-6 text-center">
        <div
          className={`text-8xl font-bold mb-2 ${getScoreColor(scoreData.score)}`}
        >
          {scoreData.score}
        </div>
        <div className="text-slate-400 text-lg mb-3">out of 100</div>
        <div
          className={`text-2xl font-semibold mb-4 ${getLevelColor(scoreData.level)}`}
        >
          {scoreData.level}
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-700 rounded-full h-4 mb-4">
          <div
            className="h-4 rounded-full transition-all duration-1000"
            style={{
              width: `${scoreData.score}%`,
              background:
                scoreData.score >= 80
                  ? "#22c55e"
                  : scoreData.score >= 50
                    ? "#eab308"
                    : "#3b82f6",
            }}
          />
        </div>
        <p className="text-slate-300">{scoreData.message}</p>
      </div>

      {/* Score Breakdown */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          📊 Score Breakdown
        </h2>
        <div className="space-y-4">
          {Object.entries(scoreData.breakdown).map(([key, data]) => (
            <div key={key}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-300 text-sm capitalize">
                  {key.replace(/_/g, " ")}
                </span>
                <span className="text-white text-sm font-semibold">
                  {data.score}/{data.max}
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2 mb-1">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${(data.score / data.max) * 100}%` }}
                />
              </div>
              <p className="text-slate-500 text-xs">{data.detail}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Strong and Weak Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            💪 Strong Areas
          </h2>
          {scoreData.strong_areas.length === 0 ? (
            <p className="text-slate-400 text-sm">
              Solve non-brute-force problems to build strong areas
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {scoreData.strong_areas.map((area) => (
                <span
                  key={area}
                  className={`text-sm px-3 py-1 rounded-full ${getApproachColor(area)}`}
                >
                  ✓ {area}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            📈 Areas to Improve
          </h2>
          {scoreData.weak_areas.length === 0 ? (
            <p className="text-green-400 text-sm">
              You have covered all approaches!
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {scoreData.weak_areas.map((area) => (
                <span
                  key={area}
                  className="text-sm px-3 py-1 rounded-full bg-slate-700 text-slate-400"
                >
                  ○ {area}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Approach Frequency */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          🎯 Approach Usage
        </h2>
        <div className="space-y-2">
          {Object.entries(scoreData.approach_frequency)
            .sort((a, b) => b[1] - a[1])
            .map(([approach, count]) => (
              <div key={approach} className="flex items-center gap-3">
                <span className="text-slate-400 text-sm w-40">{approach}</span>
                <div className="flex-1 bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{
                      width: `${(count / scoreData.total_submissions) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-slate-300 text-sm w-8 text-right">
                  {count}x
                </span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

export default ScorePage;

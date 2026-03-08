import { Link, useLocation } from "react-router-dom";

function Navbar() {
  const location = useLocation();

  const navItems = [
    { path: "/", label: "🧠 Analyze" },
    { path: "/history", label: "📜 History" },
    { path: "/score", label: "🏆 Score" },
  ];

  return (
    <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚡</span>
          <span className="text-xl font-bold text-white">Coding Coach</span>
          <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded-full">
            DL Powered
          </span>
        </div>
        <div className="flex gap-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                location.pathname === item.path
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-white hover:bg-slate-700"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;

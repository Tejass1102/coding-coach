import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const navItems = [
    { path: "/", label: "Score", icon: "⚡" },
    { path: "/history", label: "History", icon: "📜" },
  ];

  return (
    <nav style={{
      position: "sticky",
      top: 0,
      zIndex: 100,
      background: "rgba(0, 0, 0, 0.85)",
      backdropFilter: "blur(24px)",
      WebkitBackdropFilter: "blur(24px)",
      borderBottom: "1px solid rgba(255,255,255,0.08)",
    }}>
      <div style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "0 24px",
        height: "60px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>

        {/* Logo and Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: "32px", height: "32px",
            borderRadius: "8px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "16px",
            boxShadow: "0 0 16px rgba(99,102,241,0.4)",
          }}>
            ⚡
          </div>
          <span style={{ fontWeight: 700, fontSize: "16px", color: "#f1f5f9", letterSpacing: "-0.02em" }}>
            Coding Coach
          </span>
        </div>

        {/* Nav links + user info */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {navItems.map((item) => {
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: "flex", alignItems: "center", gap: "6px",
                  padding: "6px 14px",
                  borderRadius: "8px",
                  fontSize: "13px",
                  fontWeight: 500,
                  textDecoration: "none",
                  transition: "all 0.2s",
                  background: active ? "rgba(99,102,241,0.15)" : "transparent",
                  border: active ? "1px solid rgba(99,102,241,0.25)" : "1px solid transparent",
                  color: active ? "#a5b4fc" : "#94a3b8",
                  fontFamily: "'Inter', sans-serif",
                }}
                onMouseEnter={e => { if (!active) e.currentTarget.style.color = "#f1f5f9"; }}
                onMouseLeave={e => { if (!active) e.currentTarget.style.color = "#94a3b8"; }}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}

          {/* Divider */}
          <div style={{ width: 1, height: 20, background: "rgba(255,255,255,0.1)", margin: "0 4px" }} />

          {/* User email */}
          {user && (
            <span style={{
              fontSize: 12,
              color: "rgba(255,255,255,0.35)",
              maxWidth: 140,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}>
              {user.email}
            </span>
          )}

          {/* Logout button */}
          <button
            id="logout-btn"
            onClick={handleLogout}
            style={{
              padding: "6px 14px",
              borderRadius: "8px",
              fontSize: "13px",
              fontWeight: 500,
              border: "1px solid rgba(239,68,68,0.25)",
              background: "rgba(239,68,68,0.08)",
              color: "#f87171",
              cursor: "pointer",
              transition: "all 0.2s",
              fontFamily: "'Inter', sans-serif",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = "rgba(239,68,68,0.18)"; }}
            onMouseLeave={e => { e.currentTarget.style.background = "rgba(239,68,68,0.08)"; }}
          >
            Sign Out
          </button>
        </div>

      </div>
    </nav>
  );
}

export default Navbar;

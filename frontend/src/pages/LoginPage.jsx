import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setInfo("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
        navigate("/");
      } else {
        await signup(email, password);
        setInfo(
          "Account created! Check your email to confirm, then log in."
        );
        setMode("login");
      }
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.root}>
      {/* Animated background blobs */}
      <div style={styles.blob1} />
      <div style={styles.blob2} />
      <div style={styles.blob3} />

      <div style={styles.card}>
        {/* Logo / Header */}
        <div style={styles.logoRow}>
          <div style={styles.logoIcon}>⚡</div>
          <span style={styles.logoText}>Coding Coach</span>
        </div>

        <h1 style={styles.title}>
          {mode === "login" ? "Welcome back" : "Create an account"}
        </h1>
        <p style={styles.subtitle}>
          {mode === "login"
            ? "Sign in to your workspace"
            : "Start your coding journey"}
        </p>

        {/* Mode toggle pills */}
        <div style={styles.toggleRow}>
          <button
            style={{
              ...styles.toggleBtn,
              ...(mode === "login" ? styles.toggleActive : {}),
            }}
            onClick={() => { setMode("login"); setError(""); setInfo(""); }}
          >
            Sign In
          </button>
          <button
            style={{
              ...styles.toggleBtn,
              ...(mode === "signup" ? styles.toggleActive : {}),
            }}
            onClick={() => { setMode("signup"); setError(""); setInfo(""); }}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          {/* Email */}
          <div style={styles.fieldGroup}>
            <label style={styles.label} htmlFor="email">Email</label>
            <div style={styles.inputWrapper}>
              <span style={styles.inputIcon}>✉</span>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={styles.input}
                onFocus={(e) => Object.assign(e.target.style, styles.inputFocus)}
                onBlur={(e) => Object.assign(e.target.style, { boxShadow: "none", borderColor: "rgba(255,255,255,0.08)" })}
              />
            </div>
          </div>

          {/* Password */}
          <div style={styles.fieldGroup}>
            <label style={styles.label} htmlFor="password">Password</label>
            <div style={styles.inputWrapper}>
              <span style={styles.inputIcon}>🔒</span>
              <input
                id="password"
                type={showPass ? "text" : "password"}
                required
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                placeholder={mode === "signup" ? "Min. 6 characters" : "••••••••"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={styles.input}
                onFocus={(e) => Object.assign(e.target.style, styles.inputFocus)}
                onBlur={(e) => Object.assign(e.target.style, { boxShadow: "none", borderColor: "rgba(255,255,255,0.08)" })}
              />
              <button
                type="button"
                onClick={() => setShowPass((v) => !v)}
                style={styles.eyeBtn}
                tabIndex={-1}
                aria-label="Toggle password visibility"
              >
                {showPass ? "🙈" : "👁"}
              </button>
            </div>
          </div>

          {/* Error / Info messages */}
          {error && (
            <div style={styles.errorBox}>
              <span>⚠ </span>{error}
            </div>
          )}
          {info && (
            <div style={styles.infoBox}>
              <span>✅ </span>{info}
            </div>
          )}

          {/* Submit */}
          <button
            id="auth-submit-btn"
            type="submit"
            disabled={loading}
            style={{ ...styles.submitBtn, ...(loading ? styles.submitBtnDisabled : {}) }}
          >
            {loading ? (
              <span style={styles.spinnerRow}>
                <span style={styles.spinner} /> {mode === "login" ? "Signing in…" : "Creating account…"}
              </span>
            ) : (
              mode === "login" ? "Sign In →" : "Create Account →"
            )}
          </button>
        </form>

        <p style={styles.switchHint}>
          {mode === "login" ? "Don't have an account? " : "Already have an account? "}
          <button
            style={styles.switchLink}
            onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); setInfo(""); }}
          >
            {mode === "login" ? "Sign Up" : "Sign In"}
          </button>
        </p>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes blobFloat {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -20px) scale(1.05); }
          66% { transform: translate(-20px, 15px) scale(0.95); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
        #auth-submit-btn:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 8px 30px rgba(167,139,250,0.4);
        }
      `}</style>
    </div>
  );
}

const styles = {
  root: {
    minHeight: "100vh",
    background: "#060608",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px",
    position: "relative",
    overflow: "hidden",
  },
  blob1: {
    position: "absolute",
    width: 500,
    height: 500,
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(139,92,246,0.25) 0%, transparent 70%)",
    top: "-150px",
    left: "-100px",
    animation: "blobFloat 8s ease-in-out infinite",
    pointerEvents: "none",
  },
  blob2: {
    position: "absolute",
    width: 400,
    height: 400,
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(59,130,246,0.2) 0%, transparent 70%)",
    bottom: "-120px",
    right: "-80px",
    animation: "blobFloat 10s ease-in-out infinite reverse",
    pointerEvents: "none",
  },
  blob3: {
    position: "absolute",
    width: 300,
    height: 300,
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(236,72,153,0.12) 0%, transparent 70%)",
    top: "50%",
    left: "60%",
    animation: "blobFloat 12s ease-in-out infinite",
    pointerEvents: "none",
  },
  card: {
    position: "relative",
    zIndex: 1,
    width: "100%",
    maxWidth: 420,
    background: "rgba(255,255,255,0.04)",
    backdropFilter: "blur(20px)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 24,
    padding: "40px 36px",
    animation: "fadeIn 0.5s ease-out",
    boxShadow: "0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06)",
  },
  logoRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 28,
  },
  logoIcon: {
    width: 36,
    height: 36,
    background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
    borderRadius: 10,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 18,
  },
  logoText: {
    color: "#fff",
    fontWeight: 700,
    fontSize: 18,
    letterSpacing: "-0.3px",
  },
  title: {
    color: "#fff",
    fontSize: 26,
    fontWeight: 700,
    margin: "0 0 6px",
    letterSpacing: "-0.5px",
  },
  subtitle: {
    color: "rgba(255,255,255,0.45)",
    fontSize: 14,
    margin: "0 0 24px",
  },
  toggleRow: {
    display: "flex",
    background: "rgba(255,255,255,0.05)",
    borderRadius: 12,
    padding: 4,
    marginBottom: 28,
    gap: 4,
  },
  toggleBtn: {
    flex: 1,
    padding: "8px 0",
    border: "none",
    borderRadius: 9,
    background: "transparent",
    color: "rgba(255,255,255,0.45)",
    fontWeight: 500,
    fontSize: 14,
    cursor: "pointer",
    transition: "all 0.2s",
  },
  toggleActive: {
    background: "rgba(139,92,246,0.25)",
    color: "#a78bfa",
    fontWeight: 600,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 18,
  },
  fieldGroup: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  label: {
    color: "rgba(255,255,255,0.6)",
    fontSize: 13,
    fontWeight: 500,
  },
  inputWrapper: {
    position: "relative",
    display: "flex",
    alignItems: "center",
  },
  inputIcon: {
    position: "absolute",
    left: 14,
    fontSize: 14,
    opacity: 0.5,
    pointerEvents: "none",
    userSelect: "none",
  },
  input: {
    width: "100%",
    padding: "12px 40px 12px 38px",
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 12,
    color: "#fff",
    fontSize: 14,
    outline: "none",
    transition: "all 0.2s",
  },
  inputFocus: {
    boxShadow: "0 0 0 2px rgba(139,92,246,0.4)",
    borderColor: "rgba(139,92,246,0.6)",
  },
  eyeBtn: {
    position: "absolute",
    right: 12,
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: 15,
    opacity: 0.5,
    padding: "4px",
    transition: "opacity 0.2s",
  },
  errorBox: {
    background: "rgba(239,68,68,0.12)",
    border: "1px solid rgba(239,68,68,0.3)",
    borderRadius: 10,
    padding: "10px 14px",
    color: "#fca5a5",
    fontSize: 13,
  },
  infoBox: {
    background: "rgba(34,197,94,0.1)",
    border: "1px solid rgba(34,197,94,0.3)",
    borderRadius: 10,
    padding: "10px 14px",
    color: "#86efac",
    fontSize: 13,
  },
  submitBtn: {
    width: "100%",
    padding: "13px",
    background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
    border: "none",
    borderRadius: 12,
    color: "#fff",
    fontWeight: 600,
    fontSize: 15,
    cursor: "pointer",
    transition: "all 0.2s",
    marginTop: 4,
    letterSpacing: "0.2px",
  },
  submitBtnDisabled: {
    opacity: 0.6,
    cursor: "not-allowed",
    transform: "none",
  },
  spinnerRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
  },
  spinner: {
    display: "inline-block",
    width: 16,
    height: 16,
    border: "2px solid rgba(255,255,255,0.3)",
    borderTop: "2px solid #fff",
    borderRadius: "50%",
    animation: "spin 0.7s linear infinite",
  },
  switchHint: {
    textAlign: "center",
    marginTop: 24,
    color: "rgba(255,255,255,0.35)",
    fontSize: 13,
  },
  switchLink: {
    background: "none",
    border: "none",
    color: "#a78bfa",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: 13,
    padding: 0,
    textDecoration: "underline",
    textDecorationColor: "rgba(167,139,250,0.4)",
  },
};

import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import HistoryPage from "./pages/HistoryPage";
import ScorePage from "./pages/ScorePage";
import LoginPage from "./pages/LoginPage";

function AppRoutes() {
  const { user, loading } = useAuth();

  return (
    <Routes>
      {/* Public: login page — redirect to home if already logged in */}
      <Route
        path="/login"
        element={
          !loading && user ? <Navigate to="/" replace /> : <LoginPage />
        }
      />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <div style={{ minHeight: "100vh", background: "#000000" }}>
              <Navbar />
              <ScorePage />
            </div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <div style={{ minHeight: "100vh", background: "#000000" }}>
              <Navbar />
              <HistoryPage />
            </div>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;

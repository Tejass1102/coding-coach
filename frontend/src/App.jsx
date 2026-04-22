import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import HistoryPage from "./pages/HistoryPage";
import ScorePage from "./pages/ScorePage";

function App() {
  return (
    <Router>
      <div style={{ minHeight: "100vh", background: "#000000" }}>
        <Navbar />
        <Routes>
          <Route path="/" element={<ScorePage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

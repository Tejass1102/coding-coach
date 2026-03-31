# ⚡ Coding Coach

A Chrome Extension that analyzes your LeetCode code in real-time using Deep Learning — detecting algorithm patterns, explaining complexity, and giving AI-powered optimization tips.

---

## 🎯 What It Does

When you're solving a problem on LeetCode, click the **⚡ Coding Coach** button injected into the toolbar. The extension reads your code, sends it to a local backend, and shows a sidebar with:

- **Approach Detection** — identifies which algorithm pattern you used (Brute Force, Hash Map, Binary Search, etc.)
- **Approach Explanation** — plain English explanation of your approach
- **Complexity Analysis** — Time complexity, Space complexity, Difficulty level
- **Optimization Tips** — 3 AI-generated suggestions to improve your solution
- **Good Practices** — highlights what you did well
- **Save to History** — saves your submission to track progress over time

---

## 🧠 How It Works

```
Your LeetCode Code
        ↓
  Chrome Extension (content.js)
        ↓
  FastAPI Backend (localhost:8000)
        ↓
  ┌─────────────────────────────────┐
  │  Sentence Transformer           │
  │  (all-MiniLM-L6-v2)             │
  │  Code → 384-dim Embedding       │
  │       ↓                         │
  │  Zero-Shot Similarity Match     │
  │  (Cosine Sim against classes)   │
  │       +                         │
  │  Rule-Based Detection           │
  │  (nested loops, HashMap, etc.)  │
  └─────────────────────────────────┘
        ↓
  Hybrid Confidence Scoring
        ↓
  Groq LLM (llama-3.3-70b)
  → Human-readable feedback
        ↓
  Sidebar renders results
```

---

## 🏗️ Architecture

### Deep Learning Pipeline

| Component | Details |
|---|---|
| **Embedding Model** | `all-MiniLM-L6-v2` — highly efficient, CPU-friendly Sentence Transformer (384-dim vectors) |
| **Detection Method** | Zero-Shot Semantic Similarity mapped to canonical approach embeddings |
| **Hybrid Rulesengine** | Combined ML similarity matching + Symbolic rule-based heuristics (Regex, syntax parsing) |

### 8 Algorithm Classes

| Label | Class |
|---|---|
| 0 | Brute Force |
| 1 | Sliding Window |
| 2 | Dynamic Programming |
| 3 | Backtracking |
| 4 | Modified Binary Search |
| 5 | Prefix Sum |
| 6 | Hash Map |
| 7 | Two Pointers |

### Tech Stack

| Layer | Technology |
|---|---|
| Chrome Extension | Manifest V3, Vanilla JS |
| Backend | Python, FastAPI |
| DL Framework | Sentence-Transformers (`sentence-transformers`), NumPy |
| Embedding Model | MiniLM (`all-MiniLM-L6-v2`) |
| LLM Feedback | Groq API (`llama-3.3-70b-versatile`) |
| Database | Supabase (PostgreSQL) |

---

## 📁 Project Structure

```
coding-coach/
├── backend/
│   ├── main.py
│   ├── .env
│   ├── routes/
│   │   └── analyze.py
│   └── services/
│       ├── dl_analyzer.py           ← Handles MiniLM embeddings & hybrid logic
│       ├── gemini_service.py        ← Interacts with Groq API
│       ├── supabase_service.py      ← Database interactions
│       └── score_service.py         ← Interactor readiness calculations
└── extension/
    ├── manifest.json
    ├── content.js
    └── sidebar.css
```

---

## 🚀 Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/coding-coach.git
cd coding-coach
```

### 2. Set up Python backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install fastapi uvicorn sentence-transformers numpy supabase groq
```

### 3. Configure environment variables

Create `backend/.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
```

> **Get free keys:**
> - Groq API: [console.groq.com](https://console.groq.com) — free, no card required
> - Supabase: [supabase.com](https://supabase.com) — free tier

### 4. Start the backend server

```bash
cd backend
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`

### 5. Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `coding-coach/extension` folder
5. Extension is now active ✅

---

## 🧪 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/api/analyze-only` | POST | Analyze code without saving |
| `/api/save-submission` | POST | Save submission to database |
| `/api/history` | GET | Get all saved submissions |
| `/api/submission/{id}` | GET | Get single submission |
| `/api/score` | GET | Get interview readiness score |

---

## 📊 Supabase Tables

**submissions**
```
id (uuid), problem_name, language, code, created_at
```

**analyses**
```
id (uuid), submission_id (fk), predicted_approach, confidence,
approach_explanation, time_complexity, space_complexity,
optimization_tips (json), good_practices (json), difficulty_level
```

---

## 🎓 College Project Notes

This project was built as a Deep Learning application. Key logical and ML concepts demonstrated:

- **Zero-Shot Semantic Similarity** — utilizing a generalized sentence transformer (`MiniLM-L6-v2`) to compare natural language algorithmic descriptions with embedded user code, removing the need for vast datasets to train custom code-classifiers.
- **Efficient ML Deployments** — selecting a lightweight 22M parameter model allows deep learning inference to take place synchronously and efficiently entirely on a user's CPU.
- **Neurosymbolic AI Architecture** — elegantly balancing neural networks (probabilistic similarity matching) with robust symbolic software architectures (syntax and regex heuristics) for comprehensive coverage and reliability.

---

## 📝 License

MIT License — feel free to use and modify.

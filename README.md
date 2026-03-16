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
  │  CodeBERT  →  768-dim Embedding │
  │       ↓                         │
  │  Rule-Based Detection           │
  │  (nested loops, HashMap, etc.)  │
  │       ↓ (if rules unsure)       │
  │  Custom Neural Network          │
  │  Linear(768→256→64→8)           │
  └─────────────────────────────────┘
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
| **Embedding Model** | `microsoft/codebert-base` — pretrained transformer, outputs 768-dim vectors |
| **Classifier** | Custom neural network: `Linear(768→256) → BatchNorm → ReLU → Dropout(0.2) → Linear(256→64) → ReLU → Linear(64→8)` |
| **Training Data** | 96 hand-curated Java LeetCode solutions across 8 classes |
| **Hybrid Detection** | Rule-based pattern matching + ML classifier (Neurosymbolic approach) |

### 8 Algorithm Classes

| Label | Class |
|---|---|
| 0 | Brute Force |
| 1 | Sliding Window |
| 2 | Dynamic Programming |
| 3 | Greedy |
| 4 | Binary Search |
| 5 | Divide & Conquer |
| 6 | Hash Map |
| 7 | Two Pointers |

### Tech Stack

| Layer | Technology |
|---|---|
| Chrome Extension | Manifest V3, Vanilla JS |
| Backend | Python, FastAPI |
| DL Framework | PyTorch, HuggingFace Transformers |
| Embedding Model | CodeBERT (microsoft/codebert-base) |
| LLM Feedback | Groq API (llama-3.3-70b-versatile) |
| Database | Supabase (PostgreSQL) |

---

## 📁 Project Structure

```
coding-coach/
├── backend/
│   ├── main.py
│   ├── .env
│   ├── models/
│   │   └── approach_classifier.pt
│   ├── routes/
│   │   └── analyze.py
│   ├── services/
│   │   ├── codebert_service.py
│   │   ├── classifier_service.py
│   │   ├── gemini_service.py        ← uses Groq API
│   │   ├── supabase_service.py
│   │   └── score_service.py
│   └── notebooks/
│       ├── training_data.py
│       └── train_classifier.py
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

pip install fastapi uvicorn torch transformers supabase groq
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

### 4. Train the classifier (or use pretrained)

```bash
cd backend/notebooks
python train_classifier.py
```

### 5. Start the backend server

```bash
cd backend
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`

### 6. Load the Chrome Extension

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

This project was built as a Deep Learning course project. Key DL concepts demonstrated:

- **Transfer Learning** — using pretrained CodeBERT embeddings instead of training from scratch
- **Neural Network Classification** — custom MLP on top of embeddings
- **Neurosymbolic AI** — combining neural network predictions with symbolic rule-based detection for robustness
- **Class Imbalance Handling** — weighted CrossEntropyLoss based on class distribution
- **Training Regularization** — BatchNorm, Dropout, ReduceLROnPlateau scheduler

---

## 📝 License

MIT License — feel free to use and modify.

# 📖 Coding Coach — Complete Project Documentation

> A full end-to-end walkthrough of every file, every decision, and every step taken to build and deploy this project from scratch.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Directory Structure](#2-project-directory-structure)
3. [How Everything Connects (Data Flow)](#3-how-everything-connects-data-flow)
4. [Chrome Extension — File by File](#4-chrome-extension--file-by-file)
5. [Backend — File by File](#5-backend--file-by-file)
6. [Frontend Dashboard — File by File](#6-frontend-dashboard--file-by-file)
7. [The Deep Learning Pipeline](#7-the-deep-learning-pipeline)
8. [The Interview Readiness Score Algorithm](#8-the-interview-readiness-score-algorithm)
9. [Database Schema (Supabase)](#9-database-schema-supabase)
10. [Deployment — Step by Step](#10-deployment--step-by-step)
11. [Key Problems Solved During Development](#11-key-problems-solved-during-development)
12. [Dataset & Model Evaluation](#12-dataset--model-evaluation)

---

## 1. Project Overview

**Coding Coach** is a full-stack, AI-powered coding assistant designed to help students improve at LeetCode and prepare for technical interviews.

The project has three major components that work together:

| Component | What It Is | Deployed On |
|---|---|---|
| **Chrome Extension** | Injected UI on LeetCode pages | Local (Load Unpacked) |
| **Python Backend** | FastAPI REST API + AI/ML models | Hugging Face Spaces |
| **React Dashboard** | Web app to view your progress | Vercel |

### The core user journey
1. Student opens a LeetCode problem and writes some code.
2. Student clicks the **⚡ Coding Coach** button in the LeetCode toolbar.
3. The extension sends the code to the cloud backend via REST API.
4. The backend runs the code through the Deep Learning pipeline and gets AI feedback from Groq.
5. Results appear in an interactive sidebar on the LeetCode page.
6. Student clicks "Save to History." The extension sends a second request to save everything to Supabase.
7. Student opens the Vercel-hosted dashboard to see their interview readiness score, category heatmap, and recommended next challenges.

---

## 2. Project Directory Structure

```
coding-coach/
│
├── extension/                  # Chrome Extension (Manifest V3)
│   ├── manifest.json           # Extension permissions and metadata
│   ├── content.js              # Main JS injected into LeetCode pages (~750 lines)
│   ├── sidebar.css             # All styling for the sidebar UI
│   └── icons/                  # Extension icons
│
├── backend/                    # Python FastAPI Server
│   ├── main.py                 # App entrypoint — creates FastAPI app, adds CORS
│   ├── Dockerfile              # Build instructions for Hugging Face deployment
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Local secrets (NEVER commit this)
│   │
│   ├── routes/
│   │   └── analyze.py          # All 6 API route definitions
│   │
│   ├── services/
│   │   ├── dl_analyzer.py      # Sentence Transformer embedding logic
│   │   ├── classifier_service.py # Custom PyTorch approach classifier
│   │   ├── gemini_service.py   # Groq LLM analysis + Pre-Check + Verdict Tips
│   │   ├── supabase_service.py # Database read/write helpers
│   │   ├── score_service.py    # Interview Readiness Score calculation engine
│   │   └── leetcode_service.py # Live LeetCode GraphQL API calls
│   │
│   ├── models/
│   │   └── approach_classifier.pt  # The trained PyTorch model weights
│   │
│   └── data/
│       └── curated_problems.py     # Hand-curated problem lists for recommendations
│
├── frontend/                   # React Dashboard (Vite)
│   ├── index.html              # HTML shell
│   ├── vite.config.js          # Vite bundler config
│   ├── package.json            # Node dependencies
│   └── src/
│       ├── main.jsx            # React app entrypoint
│       ├── App.jsx             # Router — maps URLs to pages
│       ├── components/
│       │   └── Navbar.jsx      # Top navigation bar
│       └── pages/
│           ├── ScorePage.jsx   # Main dashboard — score, heatmap, breakdown (~590 lines)
│           └── HistoryPage.jsx # Submission history list + detail panel (~260 lines)
│
├── notebooks/                  # Jupyter notebooks for ML training
├── MODEL_EVALUATION.md         # Full dataset & model evaluation documentation
├── PROJECT_DOCUMENTATION.md    # This file
├── README.md                   # Public-facing project overview
└── DEPLOYMENT_GUIDE.md         # Detailed deployment reference
```

---

## 3. How Everything Connects (Data Flow)

### Flow 1: Analyzing Code (Extension → Backend → Extension)

```
User clicks "⚡ Coding Coach"
        │
        ▼
content.js: getCodeFromEditor()      ← reads code from Monaco editor DOM
content.js: getProblemName()         ← reads problem title from DOM
content.js: getLanguage()            ← detects Java/Python/C++/JS from code
        │
        ▼ POST /api/analyze-only
backend: routes/analyze.py
        ├─► dl_analyzer.py           ← encodes code to 384-dim vector
        ├─► classifier_service.py    ← custom PyTorch model predicts approach
        ├─► gemini_service.py        ← Groq Llama-3.3 generates human feedback
        └─► leetcode_service.py      ← fetches similar problems via GraphQL
        │
        ▼ JSON Response
content.js: renderResults()          ← builds and injects sidebar HTML
```

### Flow 2: Saving a Submission (Extension → Backend → Supabase)

```
User clicks "💾 Save to History"
        │
        ▼ POST /api/save-submission
backend: routes/analyze.py
        ├─► (runs full analysis pipeline again)
        ├─► leetcode_service.py      ← fetches problem topic tags
        ├─► supabase_service.py: save_submission()  → inserts into "submissions" table
        └─► supabase_service.py: save_analysis()    → inserts into "analyses" table
```

### Flow 3: Viewing the Dashboard (Frontend → Backend → Supabase)

```
User opens Vercel URL
        │
        ▼ GET /api/score
backend: routes/analyze.py
        └─► score_service.py: calculate_readiness_score()
                ├─► supabase_service.py: get_all_submissions()
                ├─► (runs 5-component scoring algorithm)
                └─► leetcode_service.py: fetch_daily_challenge()
        │
        ▼ JSON Response
ScorePage.jsx renders:
    - Score Ring, Level Badge
    - 5-component Score Breakdown bars
    - Category Heatmap
    - Strong/Weak Areas
    - Recommended Next Challenges
    - Daily LeetCode Challenge card
```

---

## 4. Chrome Extension — File by File

### `manifest.json`
The configuration file that Chrome reads to understand the extension.

- **`manifest_version: 3`** — Uses the latest, most secure Chrome extension API.
- **`permissions`** — Requests `activeTab`, `scripting`, and `storage` so it can interact with the open LeetCode tab.
- **`host_permissions`** — Tells Chrome which URLs the extension is allowed to make network requests to (LeetCode and the backend).
- **`content_scripts`** — Tells Chrome to automatically inject `content.js` and `sidebar.css` into any URL that matches `https://leetcode.com/problems/*`. The `run_at: document_idle` ensures the page is fully loaded before the script runs.

### `sidebar.css`
Contains all the CSS styling for the sidebar UI that appears on LeetCode. Built with a dark glassmorphism theme. Defines styles for:
- The main sidebar panel (`#coding-coach-sidebar`)
- Loading spinner animation
- All card sections (approach badge, complexity boxes, tip cards)
- Verdict cards (Accepted / WA / TLE etc.) with their color-coded styling

### `content.js` (~742 lines)
This is the entire brain of the extension. It is injected as a content script into every LeetCode problem page. Here is a breakdown of each function:

| Function | Purpose |
|---|---|
| `waitForEditor(cb)` | Polls every 1 second (up to 30 times) for the Monaco editor `.view-lines` element to appear before running the main code. |
| `getCodeFromEditor()` | Reads all `.view-line` DOM elements from Monaco and joins them into a string. This is how we extract the user's code without modifying the editor. |
| `getProblemName()` | Tries multiple DOM selectors to reliably get the problem title across different LeetCode UI versions. Falls back to `Unknown Problem`. |
| `getLanguage()` | A two-pass language detector. First tries UI dropdowns, then falls back to scanning the code itself for syntax patterns (keywords like `#include` → C++, `def` → Python, etc.). |
| `createSidebar()` | Dynamically creates the sidebar `<div>` element and appends it to `document.body`. Only creates it once. |
| `injectButton()` | Creates the ⚡ Coding Coach toolbar button and appends it to the LeetCode toolbar. If the toolbar can't be found, it falls back to a fixed-position button. |
| `analyzeCode()` | The main orchestrator: reads code, shows a loading spinner in the sidebar, makes a `POST /api/analyze-only` request, then calls `renderResults()`. |
| `renderResults(data)` | Builds the full sidebar HTML from the API response data. Creates all sections: Approach, Explanation, Complexity, Tips, Good Practices, Similar Questions, Daily Challenge. Also attaches click listeners for Save and Pre-Check buttons. |
| `scanPageForVerdict()` | Scans the LeetCode DOM for verdict text (Accepted, Wrong Answer, etc.) using both specific selectors and a broad fallback text scan of result panels. |
| `classifyVerdict(text)` | Maps raw verdict text strings to standardized labels (e.g., `"time limit"` → `"time_limit_exceeded"`). |
| `renderVerdict(verdict)` | Shows a color-coded verdict card in the sidebar. If the verdict is a failure, it makes a `POST /api/analyze-verdict` request to get specific fix tips from Groq. |
| `watchForResult()` | Sets up a `MutationObserver` that watches the entire LeetCode page for DOM changes. Whenever a verdict appears after running code, it automatically calls `renderVerdict()`. |
| **Save button listener** | Fires a `POST /api/save-submission` request when "Save to History" is clicked. |
| **Pre-Check button listener** | Fires a `POST /api/pre-check` request to get Groq's prediction on correctness before submitting to LeetCode. |

---

## 5. Backend — File by File

### `main.py`
The FastAPI application entrypoint.

- Creates the FastAPI `app` instance.
- Adds `CORSMiddleware` with `allow_origins=["*"]` so the Chrome extension and React frontend (on different domains) can call the API.
- Registers the `analyze_router` from `routes/analyze.py` under the `/api` prefix.
- Defines a root `GET /` health check endpoint.

### `Dockerfile`
Instructions for Hugging Face Spaces to build the backend environment:

1. Starts from `python:3.11-slim` base image.
2. Installs system build tools.
3. Copies `requirements.txt` and runs `pip install`.
4. Creates a writable `/.cache/huggingface` directory for model downloads.
5. Copies all backend code.
6. Exposes port `7860` (Hugging Face's default).
7. Starts the server with `uvicorn main:app --host 0.0.0.0 --port 7860`.

### `requirements.txt`
```
fastapi
uvicorn
torch
transformers
sentence-transformers
supabase
groq
python-dotenv
httpx
```

### `routes/analyze.py`
Defines all 6 API endpoints using FastAPI's `APIRouter`. Each route orchestrates calls to the service layer.

| Endpoint | Method | What It Does |
|---|---|---|
| `GET /api/score` | GET | Calls `calculate_readiness_score()` and returns the full dashboard data object. |
| `GET /api/history` | GET | Calls `get_all_submissions()` and returns the full list with nested analyses. |
| `POST /api/analyze-only` | POST | Full analysis pipeline WITHOUT saving to Supabase. Used by "⚡ Analyze" button. |
| `POST /api/save-submission` | POST | Full analysis pipeline WITH saving to Supabase. Used by "💾 Save" button. |
| `POST /api/analyze-verdict` | POST | Sends code + verdict to Groq, returns 3 specific fix tips. |
| `POST /api/pre-check` | POST | Sends code to Groq to predict correctness before running on LeetCode. |

### `services/dl_analyzer.py`
Handles code embedding using the `all-MiniLM-L6-v2` Sentence Transformer model.

- **Lazy Loading**: The model is NOT loaded when the server starts. It is only loaded into RAM on the very first API call. This lets the server bind to its port within 1 second (avoiding Render/Hugging Face deployment timeouts).
- **`get_code_embedding(code)`**: Encodes raw code text into a 384-dimensional float vector.
- **`get_embedding_summary(embedding)`**: Uses cosine similarity to compare the code's embedding against 8 canonical algorithm descriptions to find the closest semantic match (zero-shot classification).

### `services/classifier_service.py`
Runs the custom-trained PyTorch classifier model.

- **Lazy Loading**: Same pattern as `dl_analyzer.py`. The `.pt` model file is only loaded from disk on the first request.
- **`_get_classifier()`**: Loads `models/approach_classifier.pt`, rebuilds the `ApproachClassifier` neural network, loads the saved weights (`model_state_dict`), and sets it to `.eval()` mode.
- **`predict_approach(code)`**: First tries rule-based detection. If the code strongly matches a pattern (e.g., has `for i in range(len(arr))` nested loops → Brute Force), it uses that. If no confident rule fires, it runs the DL embedding + PyTorch classifier. Returns predicted approach, confidence score, and all approach probabilities.
- **`rule_based_detection(code)`**: Regex/keyword pattern matching to detect approaches deterministically.

### `services/gemini_service.py`
Handles all communication with the Groq API (`llama-3.3-70b-versatile` model). Despite the file being named "gemini" (an early naming choice), it uses the Groq API.

- **`detect_language_from_code(code)`**: Reliably detects the programming language from raw code syntax. Used because the language reported by the extension can sometimes be wrong. This ensures Groq always receives the correct language context.
- **`analyze_with_gemini(code, approach, confidence, ...)`**: The main analysis function. Constructs a detailed prompt containing the code, DL-predicted approach, confidence score, and all approach scores. Asks Groq to produce a structured 7-section response.
- **`parse_response(text)`**: Parses Groq's raw text response into a structured Python dictionary by looking for exact section headers (FINAL APPROACH, TIME COMPLEXITY, etc.).
- **`get_verdict_tips(code, verdict)`**: Given a verdict (e.g., `"time_limit_exceeded"`), constructs a targeted prompt asking Groq for 3 specific actionable fixes. Returns JSON.
- **`predict_correctness(code)`**: Sends code to Groq asking it to predict if the solution will pass, fail, TLE, or error — before the student even submits to LeetCode. Returns `prediction`, `confidence`, `summary`, and a list of `issues`.

### `services/supabase_service.py`
A thin data access layer for all Supabase database operations.

- **`save_submission(problem_name, language, code, tags)`**: Deletes any previous entry for the same problem (so only the latest attempt is stored), then inserts a new row into the `submissions` table.
- **`save_analysis(submission_id, approach_detection, analysis, ...)`**: Inserts a new row into the `analyses` table, linked to the submission by foreign key.
- **`get_all_submissions()`**: Fetches all submissions with their nested analyses in a single Supabase join query.
- **`get_submission_by_id(id)`**: Fetches a single submission record.

### `services/score_service.py`
The most complex service — a 5-component scoring engine that calculates the Interview Readiness Score. *(Full details in Section 8.)*

### `services/leetcode_service.py`
Makes live calls to LeetCode's public GraphQL API without needing authentication.

- **`fetch_problem_metadata(problem_name)`**: Given a problem name, converts it to a URL slug, then queries LeetCode's GraphQL API for the problem's `topicTags` (used for the category heatmap) and up to 3 `similarQuestions`.
- **`fetch_daily_challenge()`**: Queries LeetCode's GraphQL API for the active daily challenge and returns its title, slug, difficulty, date, and link.

---

## 6. Frontend Dashboard — File by File

### `index.html`
The HTML shell. A single `<div id="root">` that React mounts into. Imports Google Fonts (Inter).

### `vite.config.js`
Configures the Vite bundler. Simple React plugin setup.

### `src/main.jsx`
The React entry point. Mounts the `<App />` component into the `#root` div using `ReactDOM.createRoot`.

### `src/App.jsx`
Sets up client-side routing using React Router:
- `"/"` → renders `ScorePage`
- `"/history"` → renders `HistoryPage`
- Wraps everything in a black background `div`.

### `src/components/Navbar.jsx`
A fixed top navigation bar with two links: "Dashboard" and "History". Uses React Router's `<Link>` for client-side navigation.

### `src/pages/ScorePage.jsx` (~590 lines)
The main dashboard page. Fetches data from `GET /api/score` on mount.

**Sub-components defined inside this file:**

| Component | Purpose |
|---|---|
| `ScoreRing` | An SVG donut chart ring that animates to show the score (0-100). Color changes from grey → blue → amber → green based on score. |
| `DailyChallengeCard` | Displays today's LeetCode daily challenge as a clickable card. |
| `RecommendationsCard` | Shows 3 algorithmically-recommended problems targeted at the user's weak areas. |
| `BreakdownBar` | A labeled progress bar for each of the 5 score components. |
| `CategoryHeatmap` | A responsive grid of 5 category cards showing proficiency with animated fill bars. |
| `ApproachFrequency` | A horizontal bar chart of how often the user used each algorithm approach. |
| `AreasGrid` | A two-column grid showing Strong Areas (✓ colored badges) and Weak Areas (○ grey badges). |

**The `API` constant at the top** reads from the `VITE_API_URL` environment variable (set in Vercel), falling back to `http://127.0.0.1:8000/api` for local development.

### `src/pages/HistoryPage.jsx` (~260 lines)
The submission history page. Fetches data from `GET /api/history` on mount.

- **Left panel**: A scrollable list of all submissions, each showing the problem name, date, and approach badge. Clicking a row makes it the "selected" submission.
- **Right panel**: A sticky detail panel that shows the full analysis of the selected submission: approach, complexity, difficulty, and optimization tips.

---

## 7. The Deep Learning Pipeline

The backend uses a **Neurosymbolic AI** approach — combining neural network semantics with deterministic rule-based logic.

### Step 1: Code Embedding
`dl_analyzer.py` uses `all-MiniLM-L6-v2`, a 22-million parameter Sentence Transformer model that was pre-trained on hundreds of millions of sentence pairs.

- The model maps any text (including code) into a fixed-size 384-dimensional vector.
- Similar pieces of code will produce vectors that are geometrically close to each other in this 384D space.
- For each analysis, we compute the **cosine similarity** between the code's vector and 8 pre-computed canonical "approach description" vectors to get zero-shot classification scores.

### Step 2: Rule-Based Detection (Symbolic Layer)
`classifier_service.py` checks the code for explicit structural patterns before ever running the neural network:
- **Two Pointers**: `while left < right` or `left, right = 0, len` patterns.
- **Binary Search**: `mid = (left + right) // 2` or `while lo <= hi`.
- **Dynamic Programming**: `dp = [...]` table patterns.
- If a rule fires with high enough confidence, it overrides the ML model.

### Step 3: Custom PyTorch Classifier
A custom-trained feed-forward neural network (`approach_classifier.pt`):
- **Architecture**: Linear → ReLU → Dropout → Linear → ReLU → Dropout → Linear
- **Input**: 384-dimensional embedding vector from Step 1.
- **Output**: Probability distribution over N approach classes.
- **Training**: Trained on a dataset of labelled LeetCode solutions.

### Step 4: Confidence-Weighted Final Decision
Both the rule-based and ML model scores are compared. The final `predicted_approach` is selected based on a confidence threshold (`DL_CONFIDENCE_THRESHOLD`, default 60%). Groq then sees the DL result and can override it based on its own reading of the code.

---

## 8. The Interview Readiness Score Algorithm

The score is a weighted sum of 5 independent components, totalling 100 points.

### Component 1: Time-Decayed Quality (30 pts)
Uses **Exponential Moving Average (EMA)** with a 30-day half-life. A submission from 30 days ago has half the weight of a submission from today. This rewards recent, high-difficulty, non-brute-force solutions.

```
quality = difficulty_weight × (0.5 if brute_force else 1.0)
score = Σ(ema_weight × quality) / Σ(ema_weight) × 30
```

### Component 2: Consistency Frequency (20 pts)
Looks at the last 8 weeks and calculates the rolling average of active solving days per week. Solving 4+ days per week gives full marks.

### Component 3: Category Heatmap (20 pts)
Maps each submission's LeetCode topic tags to 5 core interview categories (Arrays, Trees, DP, Linked Lists, Math). Calculates the average difficulty solved per category. Rewards breadth across all categories.

### Component 4: Volume Tiers (15 pts)
Milestone-based points: 10 problems → 5 pts, 25 → 8 pts, 50 → 11 pts, 100 → 13 pts, 250 → 15 pts. Points are interpolated between milestones.

### Component 5: Optimization & Complexity (15 pts)
Parses time complexity strings (e.g., `O(N log N)`) and assigns a quality score (O(1) → 1.0, O(N²) → 0.2). Uses EMA weighting like Component 1, and penalizes brute force by 70%.

### Level Thresholds
| Score | Level |
|---|---|
| 0-19 | Newcomer |
| 20-49 | Beginner |
| 50-79 | Intermediate |
| 80-100 | Advanced |

---

## 9. Database Schema (Supabase)

Two tables are used with a one-to-many relationship.

### `submissions` table
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Auto-generated unique ID |
| `problem_name` | TEXT | e.g., "Two Sum" |
| `language` | TEXT | e.g., "python", "java" |
| `code` | TEXT | Full raw code submitted |
| `problem_tags` | TEXT[] | Array of LeetCode topic tags |
| `submitted_at` | TIMESTAMPTZ | Auto-set on insert |

### `analyses` table
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Auto-generated unique ID |
| `submission_id` | UUID (FK) | References `submissions.id` |
| `predicted_approach` | TEXT | e.g., "Dynamic Programming" |
| `confidence` | FLOAT | e.g., 87.5 |
| `all_scores` | JSONB | All approach probabilities |
| `approach_explanation` | TEXT | Groq-generated explanation |
| `time_complexity` | TEXT | e.g., "O(N)" |
| `space_complexity` | TEXT | e.g., "O(1)" |
| `optimization_tips` | TEXT[] | Array of 3 tips |
| `good_practices` | TEXT[] | Array of 2 good practices |
| `difficulty_level` | TEXT | "Beginner / Intermediate / Advanced" |

---

## 10. Deployment — Step by Step

### What Was Done

#### Phase 1: Local Development
1. Set up a Python virtual environment in `backend/venv/`.
2. Ran the FastAPI server locally with `uvicorn main:app --reload` on port 8000.
3. Built the React frontend locally with `npm run dev` on port 5173.
4. Loaded the Chrome extension via `chrome://extensions → Load Unpacked`.

#### Phase 2: Deploying the Backend (Hugging Face Spaces)
**Problem 1**: First deploy to Render failed with `ModuleNotFoundError: No module named 'sentence_transformers'`.
- **Fix**: Added `sentence-transformers` to `requirements.txt`.

**Problem 2**: Second deploy timed out — "Port scan timeout reached".
- **Root Cause**: Loading PyTorch models on startup took longer than the platform's 5-minute health check window.
- **Fix**: Implemented **Lazy Loading** in `dl_analyzer.py` and `classifier_service.py`. Models now load on the first request, not at startup. Server binds to its port in ~1 second.

**Switched to Hugging Face Spaces** for 16GB RAM (vs Render's 512MB):
1. Created a Docker Space on Hugging Face.
2. Added `SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY` as Secrets in Space settings.
3. Created `backend/Dockerfile` with `EXPOSE 7860` and Uvicorn startup command.
4. Uploaded all backend files (excluding `venv/`, `.env`, `__pycache__`, `datasets/`, `notebooks/`).
5. Space URL: `https://tejas1102-coding-coach-backend.hf.space`

#### Phase 3: Deploying the Frontend (Vercel)
1. Updated `ScorePage.jsx` and `HistoryPage.jsx` API constant to use `import.meta.env.VITE_API_URL` (env variable) instead of the hardcoded `localhost` URL.
2. Pushed changes to GitHub.
3. Imported the GitHub repo into Vercel.
4. Set Root Directory to `frontend`.
5. Added environment variable: `VITE_API_URL = https://tejas1102-coding-coach-backend.hf.space/api`.
6. Deployed. Turned off **Deployment Protection** in Vercel Settings so the URL is publicly accessible.

#### Phase 4: Connecting the Extension to Production
1. Updated `extension/content.js` line 1: `const API = "https://tejas1102-coding-coach-backend.hf.space/api"`.
2. Refreshed the extension in `chrome://extensions`.

---

## 11. Key Problems Solved During Development

| Problem | Root Cause | Solution |
|---|---|---|
| Extension can't read code | LeetCode uses Monaco editor — no `<textarea>`. Code lives in many small `.view-line` DOM spans. | Queried all `.view-line` elements and joined their `textContent`. |
| Language detection unreliable | LeetCode's UI dropdown is complex and changes across pages. | Implemented a two-pass detector: try UI → fall back to scanning code syntax patterns. |
| Sidebar disappears after running code | LeetCode re-renders the DOM when a result appears, which can displace the sidebar. | Used a `MutationObserver` to watch for DOM changes and re-attach/reopen the sidebar. |
| Verdict not detected | LeetCode's result DOM classes change frequently between updates. | Implemented a broad fallback text scan of all `[class*="result"]` panels, not just specific selectors. |
| Pre-check reports language mismatch | The extension sends `language` as a string, but it sometimes disagrees with what the code actually is. | Added `detect_language_from_code()` in `gemini_service.py` which auto-detects from syntax and overrides the frontend value. |
| Deployment timeout (Render) | PyTorch model loading on startup took 6+ minutes, exceeding the platform's 5-minute health check. | Refactored to lazy loading — models load only on the first API call, not at startup. |
| Supabase duplicate entries | Each "Save" was adding a new row for the same problem, making history messy. | Added a `delete().eq("problem_name", ...)` call before every `insert()`. |
| Vercel frontend blocked for friend | Vercel's default "Deployment Protection" locks preview deployments to the owner's account. | Disabled "Vercel Authentication" in Vercel Project Settings → Deployment Protection. |

---

## 12. Dataset & Model Evaluation

### Dataset at a Glance

| Property | Value |
|---|---|
| **Total Samples** | 446 labelled Java code snippets |
| **Classes** | 7 active approach labels |
| **Train Samples** | 385 |
| **Val Samples** | 30 |
| **Test Samples** | 31 |
| **Avg. Code Length** | ~1,885 characters/sample |
| **Format** | JSONL — one JSON object per line |

### Class Distribution (Full Dataset)

| Class | Count | % of Total | Difficulty to Learn |
|---|---|---|---|
| **Brute Force** | 178 | 39.9% | ✅ Easy (largest class, distinctive patterns) |
| **Prefix Sum** | 92 | 20.6% | ✅ Easy (good representation) |
| **Two Pointers** | 63 | 14.1% | 🟡 Medium (overlaps with Sliding Window) |
| **Dynamic Programming** | 36 | 8.1% | 🟡 Medium (distinctive `dp[]`, but few examples) |
| **Modified Binary Search** | 34 | 7.6% | 🟡 Medium (`while lo <= hi` is distinctive) |
| **Backtracking** | 23 | 5.2% | 🔴 Hard (few examples, overlaps recursion) |
| **Sliding Window** | 20 | 4.5% | 🔴 Hard (fewest examples, similar to Two Pointers) |

> ⚠️ **Class imbalance is significant.** Brute Force is nearly 40% of all data. The training pipeline uses **inverse-frequency class weighting** to compensate: `weight[i] = total / (num_classes × count[i])`. This means Sliding Window gets ~4× the gradient signal of Brute Force.

### Dataset Sources

| Source | Samples | Labelling Method |
|---|---|---|
| **Hand-crafted seed examples** (`training_data.py`) | ~150 | Manually written and labelled by the developer. Gold-standard quality. |
| **`cheehwatang/leetcode-java`** GitHub repo | ~296 | Automatically labelled via a 3-priority system: (1) filename/folder name hints, (2) LeetCode CSV topic tag mapping, (3) nested-loop brute-force heuristic. |

### Train/Val/Test Split Strategy
Splitting is done at the **problem ID level** (not sample level) to prevent data leakage. All solutions to the same problem go into the same split.

### Model Architecture

```
Input: 384-dim float vector  (all-MiniLM-L6-v2 embedding)
    │
    ▼
Linear(384 → 256)
BatchNorm1d(256)
ReLU
Dropout(p=0.2)
    │
    ▼
Linear(256 → 64)
ReLU
    │
    ▼
Linear(64 → 7)
    │
    ▼
Softmax → Probability Distribution
```

### Training Configuration

| Hyperparameter | Value |
|---|---|
| Optimizer | Adam (`weight_decay=1e-4`) |
| Learning Rate | `5e-4` |
| LR Scheduler | `ReduceLROnPlateau` (patience=5, factor=0.5) |
| Epochs | 50 |
| Batch Size | 8 |
| Loss | `CrossEntropyLoss` with class weights |

### Evaluation Metrics

All metrics use **weighted averaging** (weighted by class support) to account for the imbalanced dataset.

| Metric | Formula | What It Measures |
|---|---|---|
| **Accuracy** | Correct / Total | Overall fraction of correctly classified samples |
| **Precision (Weighted)** | TP / (TP + FP) per class | Of all predictions for a class, what fraction were correct? |
| **Recall (Weighted)** | TP / (TP + FN) per class | Of all actual samples of a class, what fraction did we catch? |
| **F1-Score (Weighted)** | `2 × (P × R) / (P + R)` | Harmonic mean — the **primary metric** for imbalanced data |

> Why F1 and not Accuracy? A classifier that always predicts "Brute Force" would achieve ~40% accuracy on this dataset without learning anything. Weighted F1 forces the model to correctly classify minority classes too.

### Expected Performance

| Metric | Expected Range |
|---|---|
| Accuracy | 65% – 80% |
| Weighted F1 | 62% – 78% |
| Precision | 60% – 80% |
| Recall | 65% – 80% |

### Confusion Matrix
Saved at `backend/notebooks/confusion_matrix.png` after running `evaluate_model.py`.

**Expected confusion pairs** (classes that get mixed up):
- **Two Pointers ↔ Sliding Window** — both use two index variables; the window expansion logic is a subtle difference.
- **Backtracking ↔ Dynamic Programming** — memoized recursion looks identical to top-down DP in code structure.
- **Brute Force ↔ Backtracking** — both use nested loops/recursion, but backtracking has pruning.

### Key Limitations

| Limitation | Impact |
|---|---|
| Small dataset (446 samples) | High variance — metrics can swing ±5–10% between runs |
| Java-only training data | May underperform on Python/C++ solutions in production |
| Frozen embeddings (not fine-tuned) | `all-MiniLM-L6-v2` was not trained on code; a code-specific encoder like CodeBERT would be more expressive |
| No `hash_map` training samples | This class was merged into `prefix_sum` during dataset construction |

> 📖 For the complete dataset construction pipeline, per-class breakdown, re-training instructions, and confusion matrix interpretation, see [MODEL_EVALUATION.md](./MODEL_EVALUATION.md).

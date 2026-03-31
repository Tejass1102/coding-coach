# ⚡ CODING COACH - QUICK REFERENCE & CHECKLIST

## 📋 Pre-Requirements Checklist

- [ ] Python 3.9+ installed
- [ ] venv activated at: `D:\College\DL\coding-coach\venv`
- [ ] LeetCode CSV downloaded to: `C:\Users\YOUR_USERNAME\Downloads\`
- [ ] leetcode-java repo cloned locally
- [ ] Groq API key obtained (https://console.groq.com)
- [ ] Supabase account created (https://supabase.com)

---

## 🗂️ Files to Download/Prepare

### 1. LeetCode CSV File

- **Source:** https://github.com/muhammadehsannaeem/Leetcode_Questions_Database
- **File:** `Leetcode_Questions_updated (2024-11-02).csv`
- **Save To:** `C:\Users\YOUR_USERNAME\Downloads\`

### 2. leetcode-java Repository

```powershell
cd D:\any\folder\you\like
git clone https://github.com/cheehwatang/leetcode-java.git
# Note the full path, e.g., D:\repos\leetcode-java
```

### 3. Update backend/.env

Already done - but verify:

```powershell
cat backend\.env
```

Should contain:

- GROQ*API_KEY=gsk*...
- SUPABASE_URL=https://...
- SUPABASE_KEY=eyJ...

---

## 🚀 STEP-BY-STEP EXECUTION

### Step 1: Environment Activation

```powershell
cd D:\College\DL\coding-coach
& .\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install sentence-transformers scikit-learn
```

### Step 2: Build Dataset

```powershell
cd backend\notebooks

# REPLACE YOUR_USERNAME with your Windows username
# REPLACE D:\repos with your actual path to leetcode-java

python build_dataset.py `
  --leetcode-csv "C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv" `
  --leetcode-java-clone "D:\repos\leetcode-java" `
  --output-dir ..\datasets `
  --spot-check-per-label 3

# Expected: Creates train.jsonl and dataset_stats.json
```

### Step 3: Train Model

```powershell
cd D:\College\DL\coding-coach\backend\notebooks

python train_classifier.py `
  --dataset-jsonl ..\datasets\train.jsonl `
  --epochs 50 `
  --batch-size 8 `
  --learning-rate 0.0005

# Expected: Creates approach_classifier.pt in models/ folder
# Takes 5-15 minutes depending on dataset size
```

### Step 4: Verify Setup

```powershell
cd D:\College\DL\coding-coach
python verify_setup.py

# Should show all ✅ marks
```

### Step 5: Start Backend Server

```powershell
cd D:\College\DL\coding-coach
python backend\main.py

# Terminal should show:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# Leave this terminal RUNNING
```

### Step 6: Test API (new terminal)

```powershell
cd D:\College\DL\coding-coach
python test_api.py

# Should show ✅ for all 3 tests
```

### Step 7: Load Chrome Extension

1. Open Chrome
2. Go to: `chrome://extensions/`
3. Toggle **Developer mode** (top-right)
4. Click **Load unpacked**
5. Select: `D:\College\DL\coding-coach\extension`
6. You should see "Coding Coach" extension in the list

### Step 8: Test on LeetCode

1. Go to: https://leetcode.com/problems/two-sum/
2. Paste some Java code in the editor
3. Look for ⚡ button near the Submit button
4. Click it
5. Sidebar should appear with analysis

---

## 🐛 Troubleshooting

| Problem                          | Solution                                              |
| -------------------------------- | ----------------------------------------------------- |
| "Module not found"               | Run: `pip install sentence-transformers scikit-learn` |
| "Model file not found"           | Run: `python backend\notebooks\train_classifier.py`   |
| "Dataset file not found"         | Run: `python backend\notebooks\build_dataset.py`      |
| "Cannot connect to backend"      | Start backend: `python backend\main.py`               |
| "CSV file not found"             | Check Windows username and CSV filename match exactly |
| "Very slow dataset building"     | Normal - building embeddings takes 5-10 minutes       |
| "Out of memory during training"  | Reduce batch size: `--batch-size 4`                   |
| "Extension button not appearing" | Wait 5 seconds after page load, refresh page          |
| "No code detected in editor"     | Make sure Monaco editor is fully loaded               |
| "API call timeout after 30s"     | Normal for first request - model loading takes time   |

---

## 📊 Expected Output Locations

After all steps complete, you should have:

```
backend/
├── .env                              ✅ Already exists
├── datasets/
│   ├── train.jsonl                  ← OUTPUT (Step 2)
│   └── dataset_stats.json           ← OUTPUT (Step 2)
├── models/
│   └── approach_classifier.pt       ← OUTPUT (Step 3)
└── main.py                          ← Run this (Step 5)
```

---

## 🧪 Testing Commands Reference

```powershell
# Activate venv
& D:\College\DL\coding-coach\venv\Scripts\Activate.ps1

# Build dataset
cd D:\College\DL\coding-coach\backend\notebooks
python build_dataset.py --leetcode-csv "C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv" --leetcode-java-clone "D:\repos\leetcode-java" --output-dir ..\datasets

# Train model
python train_classifier.py --dataset-jsonl ..\datasets\train.jsonl --epochs 50

# Verify setup
cd D:\College\DL\coding-coach
python verify_setup.py

# Start backend
python backend\main.py

# Test API (different terminal)
python test_api.py

# Check backend health
curl http://127.0.0.1:8000/
```

---

## 📈 Timeline Expectations

| Step                 | Time          | Notes                              |
| -------------------- | ------------- | ---------------------------------- |
| 1. Environment setup | 5-10 min      | pip install                        |
| 2. Build dataset     | 10-20 min     | Depends on CSV size and disk speed |
| 3. Train model       | 5-15 min      | Depends on dataset size            |
| 4. Start backend     | 2 min         | First start loads models           |
| 5-6. Testing         | 5 min         | API tests                          |
| 7. Load extension    | 2 min         | Chrome setup                       |
| 8. Test on LeetCode  | 5 min         | End-to-end test                    |
| **Total**            | **40-70 min** | **One-time setup**                 |

---

## ✅ Success Criteria

You know everything is working when:

- [x] `verify_setup.py` shows all ✅ marks
- [x] `test_api.py` passes all 3 tests
- [x] Backend running without errors at `http://127.0.0.1:8000`
- [x] Chrome extension loaded and enabled
- [x] ⚡ button appears on LeetCode problem page
- [x] Sidebar displays analysis for your code
- [x] Approach, complexity, and tips are visible

---

## 📞 Need Help?

1. **Check SETUP_GUIDE.md** for detailed explanations
2. **Run `verify_setup.py`** to diagnose issues
3. **Check terminal output** for actual error messages
4. **Ensure all file paths** use YOUR Windows username
5. **Keep backend terminal running** while testing

---

## 🎯 Next After Setup

Once everything works:

1. **Improve dataset**: Add more varied code samples
2. **Optimize model**: Tune hyperparameters in `train_classifier.py`
3. **Enhance LLM prompts**: Update prompts in `backend/services/gemini_service.py`
4. **Deploy frontend**: Set up React frontend for better UI
5. **Add more features**: History tracking, leaderboard, etc.

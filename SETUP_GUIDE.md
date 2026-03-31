# 🚀 Coding Coach - Complete Setup Guide

## Prerequisites

- Python 3.9+ installed in your venv at `D:\College\DL\coding-coach\venv`
- LeetCode CSV file downloaded
- leetcode-java repo cloned locally
- Chrome browser
- Groq API key (get free at https://console.groq.com)
- Supabase account

---

## STEP 1: Environment Setup

### 1.1 Create `.env` file in `backend/` directory

**File path:** `D:\College\DL\coding-coach\backend\.env`

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# ML Configuration
DL_CONFIDENCE_THRESHOLD=60

# Backend
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
```

### 1.2 Install required Python packages

```powershell
cd D:\College\DL\coding-coach
# Activate venv
& .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt
pip install sentence-transformers scikit-learn

# Verify installations
python -c "import torch; import transformers; import groq; print('✅ All packages installed')"
```

---

## STEP 2: Prepare Data Sources

### 2.1 Download LeetCode CSV

- Go to: https://github.com/muhammadehsannaeem/Leetcode_Questions_Database
- Download: `Leetcode_Questions_updated (2024-11-02).csv`
- Place at: `C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv`

### 2.2 Clone leetcode-java Repository

```powershell
cd D:\path\to\store\repos
git clone https://github.com/cheehwatang/leetcode-java.git
# This will be located at: D:\path\to\store\repos\leetcode-java
```

---

## STEP 3: Build Training Dataset

### 3.1 Run Dataset Builder

**Navigate to:**

```powershell
cd D:\College\DL\coding-coach
& .\venv\Scripts\Activate.ps1
cd backend\notebooks
```

**Command to run:**

```powershell
python build_dataset.py `
  --leetcode-csv "C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv" `
  --leetcode-java-clone "D:\path\to\repos\leetcode-java" `
  --output-dir ..\datasets `
  --spot-check-per-label 3
```

**Replace `YOUR_USERNAME` with your actual Windows username**

**Expected Output:**

```
✅ Loaded seed training data: 96 examples
✅ Loaded LeetCode CSV: 2xxx entries
⏳ Building dataset from leetcode-java solutions...
✅ Dataset built: XXXX total rows
  Brute Force: XXX samples
  Two Pointers: XX samples
  Sliding Window: XX samples
  [... more classes]
✅ Dataset saved to ../datasets/train.jsonl
✅ Stats saved to ../datasets/dataset_stats.json
```

### 3.2 Verify Dataset

Check if these files exist and are not empty:

- `backend/datasets/train.jsonl` (should be >1MB)
- `backend/datasets/dataset_stats.json` (should show class distribution)

```powershell
ls backend\datasets\
cat backend\datasets\dataset_stats.json
```

---

## STEP 4: Train Classifier Model

### 4.1 Run Trainer

**From:** `D:\College\DL\coding-coach\backend\notebooks`

```powershell
python train_classifier.py `
  --dataset-jsonl ..\datasets\train.jsonl `
  --epochs 50 `
  --batch-size 8 `
  --learning-rate 0.0005
```

**Expected Output:**

```
✅ Loaded 95 samples from ../datasets/train.jsonl

📊 Class distribution:
  Brute Force: 10 samples
  Two Pointers: 8 samples
  [... distribution for all 10 classes]

⏳ Loading sentence-transformers model...
✅ MiniLM loaded

⏳ Encoding code snippets...
✅ Generated embeddings: shape=(95, 384) (input_dim=384)

⚖️  Class weights: [1.0, 1.2, 0.95, ...]

🚀 Starting training...
Epoch 1/50: Loss=2.31, Train Acc=35%, Test Acc=40%
Epoch 2/50: Loss=2.15, Train Acc=45%, Test Acc=48%
...
Epoch 50/50: Loss=0.89, Train Acc=92%, Test Acc=85%

✅ Model saved to ../models/approach_classifier.pt
✅ Training complete!
```

### 4.2 Verify Model

Check if model file exists:

```powershell
ls backend\models\approach_classifier.pt -l
```

Should be approximately 1-2 MB in size.

---

## STEP 5: Verify Backend Services

### 5.1 Test Imports

```powershell
cd D:\College\DL\coding-coach
& .\venv\Scripts\Activate.ps1

python -c "
from backend.services.dl_analyzer import predict_approach
from backend.services.codebert_service import get_code_embedding
from backend.services.gemini_service import analyze_with_gemini
from backend.services.supabase_service import save_submission
print('✅ All services import successfully')
"
```

---

## STEP 6: Start Backend Server

### 6.1 Run FastAPI Backend

```powershell
cd D:\College\DL\coding-coach
& .\venv\Scripts\Activate.ps1
python backend\main.py
```

**Expected Output:**

```
⏳ Loading Approach Classifier...
✅ Approach Classifier loaded
✅ Groq configured
✅ Supabase connected

INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Press CTRL+C to quit
```

**Leave this terminal running** for the next steps.

### 6.2 Verify Backend is Running

**Open another terminal:**

```powershell
curl http://127.0.0.1:8000/
```

Should return:

```json
{ "message": "Coding Coach API is running" }
```

---

## STEP 7: Test API Endpoints

### 7.1 Test /analyze endpoint

**In a new terminal (keep backend running):**

```powershell
$body = @{
    code = '
    public class TwoSum {
        public int[] twoSum(int[] nums, int target) {
            Map<Integer, Integer> map = new HashMap<>();
            for (int i = 0; i < nums.length; i++) {
                int complement = target - nums[i];
                if (map.containsKey(complement)) {
                    return new int[] {map.get(complement), i};
                }
                map.put(nums[i], i);
            }
            return new int[] {0, 0};
        }
    }'
    language = "java"
    problem_name = "Two Sum"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/analyze" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Expected Response:**

```json
{
  "submission_id": "uuid...",
  "analysis_id": "uuid...",
  "problem_name": "Two Sum",
  "language": "java",
  "approach_detection": {
    "predicted_approach": "Hash Map",
    "confidence": 87.5
  },
  "analysis": {
    "approach_explanation": "Uses HashMap to store values and find complements...",
    "time_complexity": "O(n)",
    "space_complexity": "O(n)"
  },
  "message": "✅ Analysis saved and complete"
}
```

---

## STEP 8: Load Chrome Extension

### 8.1 Enable Extension in Chrome

1. Open Chrome
2. Go to: `chrome://extensions/`
3. Enable **Developer mode** (toggle in top-right)
4. Click **Load unpacked**
5. Select folder: `D:\College\DL\coding-coach\extension`

### 8.2 Verify Extension Loaded

- You should see **"Coding Coach"** extension in the list
- Status should show: "Enabled"

---

## STEP 9: Test End-to-End

### 9.1 Test on LeetCode

1. Go to: https://leetcode.com/problems/two-sum/
2. Write or paste Java code in the editor
3. Look for **⚡ Coding Coach** button (should appear near submit button)
4. Click it
5. A sidebar should appear with:
   - Algorithm approach detected
   - Confidence score
   - Explanation
   - Time/Space complexity
   - Optimization tips

### 9.2 Expected Result

The sidebar should show:

```
⚡ Coding Coach Analysis

Approach: Hash Map
Confidence: 87%

Explanation:
Uses a HashMap to store values seen so far and finds the
complement for the target sum in O(1) time...

Time Complexity: O(n)
Space Complexity: O(n)

Optimization Tips:
- Consider using an array instead of HashMap for range of integers
- Early return when complement is found
- ...
```

---

## STEP 10: Troubleshooting

### Issue: "Failed to load model"

- Verify `backend/models/approach_classifier.pt` exists
- Re-run training: `python train_classifier.py --dataset-jsonl ../datasets/train.jsonl`

### Issue: "No code detected"

- Ensure Monaco editor is fully loaded on LeetCode
- Wait 3 seconds after page load before clicking button

### Issue: "Backend connection failed"

- Verify backend is running: `curl http://127.0.0.1:8000/`
- Check `.env` has correct API keys
- Verify firewall allows localhost:8000

### Issue: "Dataset builder fails"

- Verify CSV file path is correct
- Verify leetcode-java folder path is correct
- Check CSV format (should have columns: _Question_No_, _Topic_tags_, _Difficulty_)

### Issue: "Training runs very slowly"

- Building embeddings takes time (5-10 minutes for 100+ samples)
- Reduce BATCH_SIZE to 4 if out of memory
- Reduce EPOCHS to 20 for testing

---

## Summary of Directories

```
D:\College\DL\coding-coach\
├── backend/
│   ├── .env                          ← CREATE THIS
│   ├── main.py                       ← Run this for backend
│   ├── requirements.txt              ← Already has dependencies
│   ├── datasets/
│   │   ├── train.jsonl               ← OUTPUT from build_dataset.py
│   │   └── dataset_stats.json        ← OUTPUT from build_dataset.py
│   ├── models/
│   │   └── approach_classifier.pt    ← OUTPUT from train_classifier.py
│   ├── routes/
│   │   └── analyze.py               ← Endpoints defined
│   ├── services/
│   │   ├── dl_analyzer.py           ← Classifier inference
│   │   ├── gemini_service.py        ← Groq API calls
│   │   ├── codebert_service.py      ← Code embeddings
│   │   └── supabase_service.py      ← Database saves
│   └── notebooks/
│       ├── build_dataset.py         ← RUN STEP 3
│       └── train_classifier.py      ← RUN STEP 4
├── extension/
│   ├── manifest.json                 ← Load this on Chrome
│   ├── content.js                    ← Injects button on LeetCode
│   └── sidebar.css
└── frontend/                          ← React UI (optional for now)
```

---

## Quick Reference Commands

```powershell
# Activate environment
& D:\College\DL\coding-coach\venv\Scripts\Activate.ps1

# Build dataset
cd D:\College\DL\coding-coach\backend\notebooks
python build_dataset.py --leetcode-csv "C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv" --leetcode-java-clone "D:\path\to\leetcode-java" --output-dir ..\datasets

# Train model
python train_classifier.py --dataset-jsonl ..\datasets\train.jsonl --epochs 50

# Start backend (from project root)
cd D:\College\DL\coding-coach
python backend\main.py

# Test API
curl http://127.0.0.1:8000/
```

---

## Next Steps After Setup

1. ✅ Run all steps above
2. ✅ Test on LeetCode.com
3. Improve dataset with more examples
4. Fine-tune model hyperparameters
5. Deploy frontend React app
6. Add more optimization suggestions in LLM prompts

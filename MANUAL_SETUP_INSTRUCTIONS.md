# 🚀 CODING COACH - COMPLETE SETUP & EXECUTION GUIDE

This file contains **everything you need** to manually set up and run the Coding Coach project.

---

## 📚 Documentation Files

I've created several reference files in the project root:

- **`SETUP_GUIDE.md`** — Detailed walkthrough with explanations (START HERE)
- **`QUICK_REFERENCE.md`** — Quick commands and checklist
- **`verify_setup.py`** — Automated verification script
- **`test_api.py`** — API endpoint testing script
- **`auto_setup.ps1`** — **Optional automated setup script** (if you want 1-click setup)
- **This file** — Overview and execution instructions

---

## ⚡ QUICK START (5 Steps)

### If you want automated setup:

```powershell
cd D:\College\DL\coding-coach
powershell -ExecutionPolicy Bypass -File auto_setup.ps1
# Then follow instructions to start backend and test
```

### If you want manual step-by-step setup:

**Follow SETUP_GUIDE.md - Steps 1-9**

---

## 📋 What You Manually Need To Do

### Before Starting:

1. **Download LeetCode CSV**
   - Go to: https://github.com/muhammadehsannaeem/Leetcode_Questions_Database
   - Download: `Leetcode_Questions_updated (2024-11-02).csv`
   - Save to: `C:\Users\YOUR_USERNAME\Downloads\`

2. **Clone leetcode-java repository**

   ```powershell
   cd D:\path\where\you\want\to\store\it
   git clone https://github.com/cheehwatang/leetcode-java.git
   # Note the full path, e.g., D:\repos\leetcode-java
   ```

3. **Get API Keys**
   - Groq: https://console.groq.com (get free key)
   - Supabase: https://supabase.com (create free project)
   - Backend/.env already has keys pre-filled, but you can update if needed

### Then Execute (Choose One):

#### OPTION A: Automated (Fastest - 1 command)

```powershell
cd D:\College\DL\coding-coach

# First, update these variables in the script if your paths differ:
# $LeetcodeCSVPath = "C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv"
# $LeetcodeJavaPath = "D:\repos\leetcode-java"

powershell -ExecutionPolicy Bypass -File auto_setup.ps1
```

#### OPTION B: Manual (Detailed - Recommended for learning)

```powershell
# Read the detailed guide
cat SETUP_GUIDE.md

# Follow steps 1-9 manually (or copy commands directly)
# Each step has exact commands to run
```

---

## 🎯 Quickest Setup Path (Copy-Paste)

```powershell
# 1. Navigate to project
cd D:\College\DL\coding-coach

# 2. Activate environment and install packages
& .\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install sentence-transformers scikit-learn

# 3. Build dataset (REPLACE paths with your actual paths)
cd backend\notebooks
python build_dataset.py `
  --leetcode-csv "D:\Coding\Leetcode_Questions.csv" `
  --leetcode-java-clone "D:\Coding\repo\leetcode-java" `
  --output-dir ..\datasets

# 4. Train model (wait 5-15 minutes)
python train_classifier.py --dataset-jsonl ..\datasets\train.jsonl --epochs 50

# 5. Verify setup
cd D:\College\DL\coding-coach
python verify_setup.py

# 6. Start backend (in FIRST terminal - keep running)
python backend\main.py

# 7. Test API (in SECOND terminal)
python test_api.py

# 8. Load extension in Chrome:
#    - chrome://extensions/
#    - Enable Developer mode
#    - Load unpacked: D:\College\DL\coding-coach\extension

# 9. Test on LeetCode
#    - https://leetcode.com/problems/two-sum/
#    - Paste code, click ⚡ button
```

---

## 🗺️ Command Map by Purpose

### Check Status

```powershell
python verify_setup.py        # Verify everything is set up
curl http://127.0.0.1:8000/  # Check if backend is running
```

### Build/Train

```powershell
cd backend\notebooks
python build_dataset.py [OPTIONS]   # Build training dataset
python train_classifier.py [OPTIONS] # Train the model
```

### Run/Test

```powershell
python backend\main.py        # Start backend server
python test_api.py            # Test API endpoints
```

### View Logs/Data

```powershell
cat backend\datasets\dataset_stats.json    # See dataset info
cat backend\.env                           # View configuration
```

---

## 📂 Key Files Overview

| File                                    | Purpose                    | You Need To                      |
| --------------------------------------- | -------------------------- | -------------------------------- |
| `SETUP_GUIDE.md`                        | Detailed walkthrough       | Read it for details              |
| `QUICK_REFERENCE.md`                    | Quick commands + checklist | Use as cheat sheet               |
| `verify_setup.py`                       | Check installation         | Run once after install           |
| `test_api.py`                           | Test API endpoints         | Run after starting backend       |
| `auto_setup.ps1`                        | Automated setup            | Run optionally                   |
| `backend/.env`                          | Config file                | Already filled, update if needed |
| `backend/main.py`                       | Backend server             | Run this to start server         |
| `backend/notebooks/build_dataset.py`    | Dataset builder            | Run once to build data           |
| `backend/notebooks/train_classifier.py` | Model trainer              | Run once to train model          |

---

## ❓ Common Questions

### Q: How long does setup take?

**A:** 40-70 minutes one-time:

- Environment setup: 5-10 min
- Dataset building: 10-20 min
- Model training: 5-15 min
- Testing: 5-10 min

### Q: Do I need to re-run setup every time?

**A:** No. After first setup:

- Just run `python backend/main.py` to start server
- Backend stays running while you use extension
- No need to rebuild dataset or retrain model

### Q: What if I see "Module not found" error?

**A:** Run: `pip install sentence-transformers scikit-learn`

### Q: What if extension button doesn't appear?

**A:**

1. Verify extension is loaded: `chrome://extensions/`
2. Refresh the LeetCode page
3. Wait 5 seconds for editor to load
4. Check browser console for errors (F12)

### Q: Backend returns 500 error?

**A:** Check:

1. Model file exists: `dir backend\models\approach_classifier.pt`
2. Dataset exists: `dir backend\datasets\train.jsonl`
3. Groq/Supabase keys in `.env` are valid

### Q: First API call is very slow?

**A:** Normal - first request loads all ML models into memory (takes ~10s). Subsequent requests are fast.

---

## ✅ Verification Checklist

After each step, verify:

- [ ] Step 1: All pip packages installed without errors
- [ ] Step 2: `backend/datasets/train.jsonl` exists (>1MB)
- [ ] Step 2: `backend/datasets/dataset_stats.json` created
- [ ] Step 3: `backend/models/approach_classifier.pt` exists (1-2MB)
- [ ] Step 4: `verify_setup.py` shows all ✅
- [ ] Step 5: Backend running at `http://127.0.0.1:8000`
- [ ] Step 6: `test_api.py` passes all 3 tests
- [ ] Step 7: Extension loaded and enabled in Chrome
- [ ] Step 8: ⚡ button visible on LeetCode
- [ ] Step 8: Sidebar shows analysis after clicking button

---

## 🐛 If Something Fails

### Check in this order:

1. **Re-read the error message** - usually it's very clear
2. **Run `verify_setup.py`** - shows what's missing
3. **Check file paths** - Windows usernames must match exactly
4. **Check backend logs** - run `python backend/main.py` and watch terminal
5. **Check browser console** - F12 on LeetCode, look for errors
6. **Check `.env` file** - make sure API keys are valid

### Common error solutions:

```powershell
# "Model not found"
python backend\notebooks\train_classifier.py --dataset-jsonl ..\datasets\train.jsonl

# "Dataset not found"
cd backend\notebooks
python build_dataset.py --leetcode-csv "..." --leetcode-java-clone "..." --output-dir ..\datasets

# "Import error"
pip install -r backend\requirements.txt
pip install sentence-transformers scikit-learn

# "Connection refused"
python backend\main.py  # Start backend in another terminal
```

---

## 🎓 Learning Path

After setup works, explore:

1. **`backend/services/dl_analyzer.py`** — How ML classification works
2. **`backend/routes/analyze.py`** — API endpoint logic
3. **`extension/content.js`** — How extension communicates with backend
4. **`backend/services/gemini_service.py`** — How LLM generates feedback

---

## 📞 Support Resources

- **Detailed guide:** `SETUP_GUIDE.md` (read first)
- **Quick ref:** `QUICK_REFERENCE.md` (bookmark this)
- **Verify:** `python verify_setup.py` (diagnose issues)
- **Test:** `python test_api.py` (check API working)
- **Auto-setup:** `auto_setup.ps1` (one-click install)

---

## 🎯 Next Steps After Setup Works

1. ✅ Run all setup steps above
2. ✅ Test on LeetCode.com with sample code
3. 🔄 Improve dataset with more code examples
4. 🔄 Fine-tune model (adjust EPOCHS, BATCH_SIZE)
5. 🔄 Modify LLM prompts for better feedback
6. 🚀 Deploy frontend UI
7. 🚀 Publish extension to Chrome Web Store

---

## 📞 You're All Set!

Once you complete all steps:

```
✅ Dataset built
✅ Model trained
✅ Backend running
✅ Extension loaded
✅ API working
✅ All tests passing
```

You're ready to analyze LeetCode code in real-time! 🎉

---

**Start with:** `cat SETUP_GUIDE.md` and follow step-by-step

**Questions?** Check `QUICK_REFERENCE.md` first

**Need help?** Run `python verify_setup.py` to diagnose

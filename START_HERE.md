# ⚡ START HERE - Coding Coach Setup

Welcome! You need to manually set up the Coding Coach project. All code and instructions are ready for you.

---

## 📖 READ THESE FILES IN THIS ORDER

### 1️⃣ **Start with:** `MANUAL_SETUP_INSTRUCTIONS.md`

- Overview of what needs to be done
- Quick start options (automated or manual)
- Common questions answered
- Choose your setup path here

### 2️⃣ **For detailed steps:** `SETUP_GUIDE.md`

- Step-by-step walkthrough with explanations
- Every command to run
- Expected outputs
- Troubleshooting guide

### 3️⃣ **For quick reference:** `QUICK_REFERENCE.md`

- Checklist format
- Commands you can copy-paste
- Expected timelines
- Success criteria

---

## 🚀 FASTEST SETUP (Choose One)

### Option A: One-Click Automated Setup ⚡

```powershell
# Update these paths if yours are different:
$LeetcodeCSVPath = "C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv"
$LeetcodeJavaPath = "D:\repos\leetcode-java"

cd D:\College\DL\coding-coach
powershell -ExecutionPolicy Bypass -File auto_setup.ps1
```

### Option B: Manual Copy-Paste Setup 📋

Follow any section in `SETUP_GUIDE.md` and copy the commands

### Option C: Read Everything First 📚

Read `MANUAL_SETUP_INSTRUCTIONS.md` completely, then do the steps

---

## 🎯 WHAT YOU NEED BEFORE STARTING

Before running any setup, prepare these:

- [ ] **LeetCode CSV File**
  - Download from: https://github.com/muhammadehsannaeem/Leetcode_Questions_Database
  - Save to: `C:\Users\YOUR_USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv`

- [ ] **leetcode-java Repository**
  - Clone with: `git clone https://github.com/cheehwatang/leetcode-java.git`
  - Note the full path where you clone it

- [ ] **API Keys** (skip if using pre-filled .env)
  - Groq API key: https://console.groq.com
  - Supabase credentials: https://supabase.com

---

## 📋 STEP-BY-STEP SUMMARY

1. **Read:** `MANUAL_SETUP_INSTRUCTIONS.md` (5 min read)
2. **Prepare:** Download CSV and clone leetcode-java (10 min)
3. **Run:** Either automated script OR follow SETUP_GUIDE.md (40-60 min)
4. **Verify:** Run `verify_setup.py` (5 min)
5. **Test:** Run `test_api.py` (5 min)
6. **Use:** Load extension in Chrome and test on LeetCode

---

## ✅ SUCCESS CRITERIA

You know everything works when:

```
✅ verify_setup.py shows all green checks
✅ test_api.py passes all 3 tests
✅ Backend running at http://127.0.0.1:8000
✅ ⚡ button appears on LeetCode
✅ Sidebar shows analysis when code is submitted
```

---

## 📂 FILE GUIDE

| File                           | Purpose                    | When to Use                |
| ------------------------------ | -------------------------- | -------------------------- |
| `MANUAL_SETUP_INSTRUCTIONS.md` | **Overview & quick start** | **READ FIRST**             |
| `SETUP_GUIDE.md`               | Detailed walkthrough       | For step-by-step guidance  |
| `QUICK_REFERENCE.md`           | Quick commands & checklist | After reading guide        |
| `verify_setup.py`              | Diagnose issues            | After environment setup    |
| `test_api.py`                  | Test API endpoints         | After starting backend     |
| `auto_setup.ps1`               | One-click automated setup  | Use if you want automation |

---

## 🎬 GET STARTED NOW

### For Automation:

```powershell
cd D:\College\DL\coding-coach
powershell -ExecutionPolicy Bypass -File auto_setup.ps1
```

### For Manual Setup:

```powershell
# Read the guide
cat MANUAL_SETUP_INSTRUCTIONS.md

# Or start with detailed guide
cat SETUP_GUIDE.md
```

### For Verification:

```powershell
python verify_setup.py
```

---

## 💡 TIPS

- **Keep a terminal open** for the backend server (it needs to stay running)
- **Use separate terminals** for running commands in parallel
- **Check your Windows username** - it must match in CSV path
- **First API call is slow** - model loading takes ~10-15s
- **Don't close backend terminal** - extension needs it to communicate

---

## 📞 QUICK TROUBLESHOOTING

| Issue                      | Solution                                                    |
| -------------------------- | ----------------------------------------------------------- |
| "Module not found"         | `pip install sentence-transformers scikit-learn`            |
| "Cannot find CSV"          | Check Windows username in path matches YOUR actual username |
| "Model not found"          | Run: `python backend\notebooks\train_classifier.py`         |
| "Backend not responding"   | Start it: `python backend\main.py`                          |
| "No ⚡ button on LeetCode" | Load extension: `chrome://extensions/`                      |
| "Very slow first request"  | Normal - give it 15-30 seconds                              |

---

## 🎓 LEARNING RESOURCES

After setup works:

- Explore `backend/services/` to understand ML pipeline
- Check `extension/content.js` to see how extension works
- Review `backend/routes/analyze.py` for API logic
- Read `backend/services/gemini_service.py` for LLM integration

---

**👉 NEXT STEP: Read `MANUAL_SETUP_INSTRUCTIONS.md`**

Questions? Everything is covered in the setup guides. Check there first!

Estimated total time: **1-1.5 hours** (one-time setup)

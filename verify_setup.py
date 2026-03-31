"""
Quick test script to verify everything is set up correctly
Run from: D:\College\DL\coding-coach
"""

import os
import sys

print("=" * 60)
print("🔍 Coding Coach Setup Verification")
print("=" * 60)

# Check 1: Python packages
print("\n✓ Checking Python packages...")
try:
    import torch
    print(f"  ✅ PyTorch version: {torch.__version__}")
except ImportError:
    print("  ❌ PyTorch not installed - run: pip install torch")
    sys.exit(1)

try:
    import transformers
    print(f"  ✅ Transformers version: {transformers.__version__}")
except ImportError:
    print("  ❌ Transformers not installed - run: pip install transformers")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    print("  ✅ Sentence-transformers installed")
except ImportError:
    print("  ❌ Sentence-transformers not installed - run: pip install sentence-transformers")
    sys.exit(1)

try:
    import groq
    print("  ✅ Groq installed")
except ImportError:
    print("  ❌ Groq not installed - run: pip install groq")
    sys.exit(1)

try:
    import supabase
    print("  ✅ Supabase installed")
except ImportError:
    print("  ❌ Supabase not installed - run: pip install supabase")
    sys.exit(1)

try:
    from fastapi import FastAPI
    print("  ✅ FastAPI installed")
except ImportError:
    print("  ❌ FastAPI not installed - run: pip install fastapi uvicorn")
    sys.exit(1)

# Check 2: .env file
print("\n✓ Checking .env configuration...")
env_path = "backend/.env"
if os.path.exists(env_path):
    print(f"  ✅ .env file found at {env_path}")
    with open(env_path, 'r') as f:
        env_content = f.read()
        if "GROQ_API_KEY" in env_content:
            print("  ✅ GROQ_API_KEY configured")
        else:
            print("  ⚠️  GROQ_API_KEY not set - update backend/.env")
        if "SUPABASE_URL" in env_content and "SUPABASE_KEY" in env_content:
            print("  ✅ SUPABASE credentials configured")
        else:
            print("  ⚠️  SUPABASE credentials not set - update backend/.env")
else:
    print(f"  ❌ .env file not found at {env_path}")
    sys.exit(1)

# Check 3: Models and datasets
print("\n✓ Checking trained model and datasets...")
model_path = "backend/models/approach_classifier.pt"
if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"  ✅ Model found at {model_path} ({size_mb:.1f} MB)")
else:
    print(f"  ⚠️  Model not found at {model_path}")
    print("     You need to run: python backend/notebooks/train_classifier.py")

dataset_path = "backend/datasets/train.jsonl"
if os.path.exists(dataset_path):
    size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
    lines = sum(1 for _ in open(dataset_path))
    print(f"  ✅ Dataset found at {dataset_path} ({size_mb:.1f} MB, {lines} samples)")
else:
    print(f"  ⚠️  Dataset not found at {dataset_path}")
    print("     You need to run: python backend/notebooks/build_dataset.py")

# Check 4: Backend files
print("\n✓ Checking backend structure...")
required_files = [
    "backend/main.py",
    "backend/routes/analyze.py",
    "backend/services/classifier_service.py",
    "backend/services/gemini_service.py",
    "backend/services/dl_analyzer.py",
    "backend/services/supabase_service.py",
]
for file_path in required_files:
    if os.path.exists(file_path):
        print(f"  ✅ {file_path}")
    else:
        print(f"  ❌ {file_path} MISSING")

# Check 5: Extension files
print("\n✓ Checking Chrome extension...")
required_ext_files = [
    "extension/manifest.json",
    "extension/content.js",
    "extension/sidebar.css",
]
for file_path in required_ext_files:
    if os.path.exists(file_path):
        print(f"  ✅ {file_path}")
    else:
        print(f"  ❌ {file_path} MISSING")

print("\n" + "=" * 60)
print("✅ SETUP VERIFICATION COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("  1. If model not found: python backend/notebooks/train_classifier.py")
print("  2. If dataset not found: python backend/notebooks/build_dataset.py")
print("  3. Start backend: python backend/main.py")
print("  4. Load extension on Chrome: chrome://extensions/")
print("  5. Test on: https://leetcode.com/problems/two-sum/")
print("=" * 60)

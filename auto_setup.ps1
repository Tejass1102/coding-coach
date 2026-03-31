# Automated Setup Script for Coding Coach
# Run this from: D:\College\DL\coding-coach
# Usage: powershell -ExecutionPolicy Bypass -File auto_setup.ps1

param(
    [string]$LeetcodeCSVPath = "C:\Users\$env:USERNAME\Downloads\Leetcode_Questions_updated (2024-11-02).csv",
    [string]$LeetcodeJavaPath = "D:\repos\leetcode-java"
)

$ProjectRoot = Get-Location
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Header {
    param([string]$Text)
    Write-Host "`n$('=' * 70)" -ForegroundColor Cyan
    Write-Host "⚡ $Text" -ForegroundColor Green
    Write-Host "$('=' * 70)`n" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Text)
    Write-Host "🔹 $Text" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

Write-Header "CODING COACH - AUTOMATED SETUP"

# Check if paths exist
Write-Step "Verifying paths..."

if ($LeetcodeCSVPath -and (Test-Path $LeetcodeCSVPath)) {
    Write-Success "LeetCode CSV found at: $LeetcodeCSVPath"
} else {
    Write-Error "LeetCode CSV NOT found at: $LeetcodeCSVPath"
    Write-Host "Please download from: https://github.com/muhammadehsannaeem/Leetcode_Questions_Database"
    exit 1
}

if ($LeetcodeJavaPath -and (Test-Path $LeetcodeJavaPath)) {
    Write-Success "leetcode-java repo found at: $LeetcodeJavaPath"
} else {
    Write-Error "leetcode-java repo NOT found at: $LeetcodeJavaPath"
    Write-Host "Clone with: git clone https://github.com/cheehwatang/leetcode-java.git"
    exit 1
}

# Step 1: Activate venv and install packages
Write-Header "STEP 1: ENVIRONMENT SETUP"

Write-Step "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Step "Installing Python packages..."
pip install -q -r backend\requirements.txt
pip install -q sentence-transformers scikit-learn

Write-Success "Environment ready"

# Step 2: Build dataset
Write-Header "STEP 2: BUILDING DATASET"

Write-Step "Creating dataset from LeetCode data..."
Push-Location backend\notebooks

python build_dataset.py `
    --leetcode-csv $LeetcodeCSVPath `
    --leetcode-java-clone $LeetcodeJavaPath `
    --output-dir ..\datasets `
    --spot-check-per-label 3

if (Test-Path ..\datasets\train.jsonl) {
    $size = (Get-Item ..\datasets\train.jsonl).Length / 1MB
    Write-Success "Dataset created: train.jsonl ($([math]::Round($size, 2)) MB)"
} else {
    Write-Error "Dataset creation failed"
    exit 1
}

Pop-Location

# Step 3: Train model
Write-Header "STEP 3: TRAINING CLASSIFIER MODEL"

Write-Step "Training neural network classifier..."
Push-Location backend\notebooks

python train_classifier.py `
    --dataset-jsonl ..\datasets\train.jsonl `
    --epochs 50 `
    --batch-size 8

if (Test-Path ..\models\approach_classifier.pt) {
    $size = (Get-Item ..\models\approach_classifier.pt).Length / 1MB
    Write-Success "Model trained and saved: approach_classifier.pt ($([math]::Round($size, 2)) MB)"
} else {
    Write-Error "Model training failed"
    exit 1
}

Pop-Location

# Step 4: Verify setup
Write-Header "STEP 4: VERIFYING SETUP"

Push-Location $ProjectRoot
python verify_setup.py

Pop-Location

# Step 5: Summary
Write-Header "✅ SETUP COMPLETE"

Write-Host @"
🎉 All setup steps completed successfully!

Next steps:
1. Start the backend server:
   - Open a new PowerShell terminal
   - Run: python backend\main.py

2. Test the API (in another terminal):
   - Run: python test_api.py

3. Load Chrome extension:
   - Go to: chrome://extensions/
   - Enable Developer mode
   - Click "Load unpacked"
   - Select: D:\College\DL\coding-coach\extension

4. Test on LeetCode:
   - Go to: https://leetcode.com/problems/two-sum/
   - Write some Java code
   - Click the ⚡ button

Need help? Check:
  - SETUP_GUIDE.md (detailed guide)
  - QUICK_REFERENCE.md (quick commands)

"@

Write-Host "Setup timestamp: $timestamp" -ForegroundColor Gray

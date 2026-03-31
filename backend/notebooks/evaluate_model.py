import sys
import os
sys.path.append(os.path.abspath(".."))

import torch
import torch.nn as nn
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    ConfusionMatrixDisplay
)
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns

from services.codebert_service import get_code_embedding
from notebooks.training_data import data, LABEL_NAMES

# ── Load Model ────────────────────────────────────────────
class ApproachClassifier(nn.Module):
    def __init__(self, input_dim=768, num_classes=8):
        super(ApproachClassifier, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )
    def forward(self, x):
        return self.network(x)

print("⏳ Loading model...")
checkpoint = torch.load("../models/approach_classifier.pt", map_location="cpu", weights_only=False)
model = ApproachClassifier(
    input_dim=checkpoint["input_dim"],
    num_classes=checkpoint["num_classes"]
)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
label_names = checkpoint["label_names"]
print("✅ Model loaded\n")

# ── Get Embeddings ────────────────────────────────────────
print("⏳ Generating embeddings for all samples...")
embeddings = []
labels = []

for i, (code, label) in enumerate(data):
    emb = get_code_embedding(code)
    embeddings.append(emb)
    labels.append(label)
    if (i + 1) % 10 == 0:
        print(f"  {i + 1}/{len(data)} done...")

X = np.array(embeddings)
y = np.array(labels)
print(f"✅ Embeddings done — shape: {X.shape}\n")

# ── Train/Test Split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"📊 Train samples: {len(X_train)}")
print(f"📊 Test samples:  {len(X_test)}\n")

# ── Predict ───────────────────────────────────────────────
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
with torch.no_grad():
    outputs = model(X_test_tensor)
    probs = torch.softmax(outputs, dim=1).numpy()
    y_pred = np.argmax(probs, axis=1)

# ── Evaluation Metrics ────────────────────────────────────
label_list = [label_names[i] for i in range(len(label_names))]

accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
recall    = recall_score(y_test, y_pred, average="weighted", zero_division=0)
f1        = f1_score(y_test, y_pred, average="weighted", zero_division=0)

print("=" * 55)
print("           📊 EVALUATION METRICS")
print("=" * 55)
print(f"  Accuracy   : {accuracy  * 100:.2f}%")
print(f"  Precision  : {precision * 100:.2f}%")
print(f"  Recall     : {recall    * 100:.2f}%")
print(f"  F1 Score   : {f1        * 100:.2f}%")
print("=" * 55)
print()

# ── Per Class Report ──────────────────────────────────────
print("📋 Per-Class Classification Report:")
print("-" * 55)
print(classification_report(
    y_test, y_pred,
    target_names=label_list,
    zero_division=0
))

# ── Confusion Matrix ──────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(10, 8))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=label_list,
    yticklabels=label_list
)
plt.title("Confusion Matrix — Coding Coach Classifier", fontsize=14, pad=15)
plt.ylabel("Actual Label", fontsize=11)
plt.xlabel("Predicted Label", fontsize=11)
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.show()
print("✅ Confusion matrix saved as confusion_matrix.png")

# ── Per Class Accuracy ────────────────────────────────────
print("\n📊 Per-Class Accuracy:")
print("-" * 40)
for i, name in enumerate(label_list):
    mask = y_test == i
    if mask.sum() > 0:
        class_acc = accuracy_score(y_test[mask], y_pred[mask])
        correct   = (y_pred[mask] == i).sum()
        total     = mask.sum()
        print(f"  {name:<22} {class_acc * 100:5.1f}%  ({correct}/{total})")
    else:
        print(f"  {name:<22}   N/A  (no test samples)")

# ── Confidence Analysis ───────────────────────────────────
print("\n📊 Average Prediction Confidence:")
print("-" * 40)
for i, name in enumerate(label_list):
    mask = y_pred == i
    if mask.sum() > 0:
        avg_conf = probs[mask, i].mean() * 100
        print(f"  {name:<22} {avg_conf:5.1f}%")

print("\n✅ Evaluation complete!")

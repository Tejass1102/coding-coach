import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import torch
import torch.nn as nn
import numpy as np
from collections import Counter
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from training_data import data, LABEL_NAMES

# ─── Config ───────────────────────────────────────────
EPOCHS = 50
BATCH_SIZE = 8
LEARNING_RATE = 5e-4
NUM_CLASSES = 6
MODEL_SAVE_PATH = "../models/approach_classifier.pt"

# ─── Load CodeBERT ────────────────────────────────────
print("⏳ Loading CodeBERT...")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
codebert = AutoModel.from_pretrained("microsoft/codebert-base")
codebert.eval()
print("✅ CodeBERT loaded")

# ─── Generate Embeddings ──────────────────────────────
def get_embedding(code: str) -> np.ndarray:
    inputs = tokenizer(
        code,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )
    with torch.no_grad():
        outputs = codebert(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()

print("⏳ Generating embeddings for all training samples...")
embeddings = []
labels = []
for code, label in data:
    emb = get_embedding(code)
    embeddings.append(emb)
    labels.append(label)

embeddings = np.array(embeddings)
labels = np.array(labels)
print(f"✅ Generated {len(embeddings)} embeddings")

# Print class distribution so we can see imbalance
label_counts = Counter(labels.tolist())
print("\n📊 Class distribution:")
for label_idx, count in sorted(label_counts.items()):
    print(f"  {LABEL_NAMES[label_idx]}: {count} samples")

# ─── Dataset ──────────────────────────────────────────
class CodeDataset(Dataset):
    def __init__(self, embeddings, labels):
        self.X = torch.tensor(embeddings, dtype=torch.float32)
        self.y = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

X_train, X_test, y_train, y_test = train_test_split(
    embeddings, labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)

train_dataset = CodeDataset(X_train, y_train)
test_dataset = CodeDataset(X_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# ─── Classifier Model ─────────────────────────────────
class ApproachClassifier(nn.Module):
    def __init__(self, input_dim=768, num_classes=6):
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

model = ApproachClassifier()

# ─── Class Weights ────────────────────────────────────
# Gives more importance to underrepresented classes
# This fixes the Brute Force vs DP confusion
total = len(labels)
weights = torch.tensor([
    total / (NUM_CLASSES * label_counts[i])
    for i in range(NUM_CLASSES)
], dtype=torch.float32)
print(f"\n⚖️  Class weights: {[round(w.item(), 2) for w in weights]}")

criterion = nn.CrossEntropyLoss(weight=weights)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)

# Learning rate scheduler
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', patience=5, factor=0.5
)

# ─── Training Loop ────────────────────────────────────
print("\n🚀 Starting training...")

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    correct = 0
    total_samples = 0

    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == batch_y).sum().item()
        total_samples += batch_y.size(0)

    scheduler.step(total_loss)
    accuracy = 100 * correct / total_samples

    if (epoch + 1) % 5 == 0:
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss:.4f} | Accuracy: {accuracy:.1f}%")

# ─── Evaluation ───────────────────────────────────────
print("\n📊 Evaluating on test set...")
model.eval()
all_preds = []
all_labels = []

with torch.no_grad():
    for batch_X, batch_y in test_loader:
        outputs = model(batch_X)
        _, predicted = torch.max(outputs, 1)
        all_preds.extend(predicted.numpy())
        all_labels.extend(batch_y.numpy())

print(classification_report(
    all_labels,
    all_preds,
    target_names=list(LABEL_NAMES.values()),
    zero_division=0
))

# ─── Save ─────────────────────────────────────────────
os.makedirs("../models", exist_ok=True)
torch.save({
    "model_state_dict": model.state_dict(),
    "input_dim": 768,
    "num_classes": NUM_CLASSES,
    "label_names": LABEL_NAMES
}, MODEL_SAVE_PATH)
print(f"✅ Model saved to {MODEL_SAVE_PATH}")
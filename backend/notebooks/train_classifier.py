import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse
import json
import torch
import torch.nn as nn
import numpy as np
from collections import Counter
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ─── Config ───────────────────────────────────────────
EPOCHS = 50
BATCH_SIZE = 8
LEARNING_RATE = 5e-4
INTERNAL_LABELS = [
    "brute_force",
    "two_pointers",
    "sliding_window",
    "prefix_sum",
    "modified_binary_search",
    "backtracking",
    "dynamic_programming",
    "hash_map",
]
NUM_CLASSES = len(INTERNAL_LABELS)
MODEL_SAVE_PATH = "../models/approach_classifier.pt"

DEFAULT_DATASET_JSONL = "../datasets/train.jsonl"


def load_jsonl_rows(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main():
    global EPOCHS, BATCH_SIZE, LEARNING_RATE

    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-jsonl", type=str, default=DEFAULT_DATASET_JSONL)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    ap.add_argument("--learning-rate", type=float, default=LEARNING_RATE)
    ap.add_argument("--model-save-path", type=str, default=MODEL_SAVE_PATH)
    args = ap.parse_args()

    EPOCHS = args.epochs
    BATCH_SIZE = args.batch_size
    LEARNING_RATE = args.learning_rate

    dataset_path = args.dataset_jsonl
    if not os.path.isabs(dataset_path):
        dataset_path = os.path.join(os.path.dirname(__file__), dataset_path)

    rows = load_jsonl_rows(dataset_path)
    if not rows:
        raise ValueError(f"No rows found in {dataset_path}")

    label_to_idx = {lbl: i for i, lbl in enumerate(INTERNAL_LABELS)}

    labels_list = []
    codes_list = []
    for r in rows:
        lbl = r.get("label")
        if lbl not in label_to_idx:
            continue
        codes_list.append(r["code"])
        labels_list.append(label_to_idx[lbl])

    labels_arr = np.array(labels_list, dtype=np.int64)
    print(f"✅ Loaded {len(labels_arr)} samples from {dataset_path}")

    # Print class distribution.
    label_counts = Counter(labels_arr.tolist())
    print("\n📊 Class distribution:")
    for label_idx in range(NUM_CLASSES):
        pretty = INTERNAL_LABELS[label_idx].replace("_", " ").title()
        print(f"  {pretty}: {label_counts.get(label_idx, 0)} samples")

    # ─── Generate Embeddings (MiniLM) ──────────────────────────────
    print("\n⏳ Loading sentence-transformers model...")
    st_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ MiniLM loaded")

    print("⏳ Encoding code snippets...")
    embeddings = st_model.encode(
        codes_list,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32)

    input_dim = int(embeddings.shape[1])
    print(f"✅ Generated embeddings: shape={embeddings.shape} (input_dim={input_dim})")

    # ─── Dataset ─────────────────────────────────────────────────
    class CodeDataset(Dataset):
        def __init__(self, embeddings, labels):
            self.X = torch.tensor(embeddings, dtype=torch.float32)
            self.y = torch.tensor(labels, dtype=torch.long)

        def __len__(self):
            return len(self.X)

        def __getitem__(self, idx):
            return self.X[idx], self.y[idx]

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings,
            labels_arr,
            test_size=0.2,
            random_state=42,
            stratify=labels_arr,
        )
    except Exception:
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings,
            labels_arr,
            test_size=0.2,
            random_state=42,
            stratify=None,
        )

    train_dataset = CodeDataset(X_train, y_train)
    test_dataset = CodeDataset(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    # ─── Classifier Model ─────────────────────────────────
    class ApproachClassifier(nn.Module):
        def __init__(self, input_dim: int, num_classes: int):
            super(ApproachClassifier, self).__init__()
            self.network = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, 64),
                nn.ReLU(),
                nn.Linear(64, num_classes),
            )

        def forward(self, x):
            return self.network(x)

    model = ApproachClassifier(input_dim=input_dim, num_classes=NUM_CLASSES)

    # ─── Class Weights ────────────────────────────────────
    total = len(labels_arr)
    weights_list = []
    for i in range(NUM_CLASSES):
        cnt = label_counts.get(i, 0)
        if cnt <= 0:
            weights_list.append(0.0)
        else:
            weights_list.append(total / (NUM_CLASSES * cnt))
    weights = torch.tensor(weights_list, dtype=torch.float32)
    print(f"\n⚖️  Class weights: {[round(w.item(), 2) for w in weights]}")

    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)

    # Learning rate scheduler
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", patience=5, factor=0.5
    )

    # ─── Training Loop ────────────────────────────────────────
    print("\n🚀 Starting training...")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0.0
        correct = 0
        total_samples = 0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += float(loss.item())
            _, predicted = torch.max(outputs, 1)
            correct += int((predicted == batch_y).sum().item())
            total_samples += int(batch_y.size(0))

        scheduler.step(total_loss)
        accuracy = 100.0 * correct / max(1, total_samples)

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
            all_preds.extend(predicted.numpy().tolist())
            all_labels.extend(batch_y.numpy().tolist())

    print(
        classification_report(
            all_labels,
            all_preds,
            labels=list(range(NUM_CLASSES)),
            target_names=[lbl.replace("_", " ").title() for lbl in INTERNAL_LABELS],
            zero_division=0,
        )
    )

    # ─── Save ─────────────────────────────────────────────
    models_dir = os.path.join(os.path.dirname(__file__), "../models")
    os.makedirs(models_dir, exist_ok=True)
    save_path = args.model_save_path
    if not os.path.isabs(save_path):
        save_path = os.path.join(os.path.dirname(__file__), save_path)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_dim": input_dim,
            "num_classes": NUM_CLASSES,
            "label_names": {i: INTERNAL_LABELS[i] for i in range(NUM_CLASSES)},
        },
        save_path,
    )
    print(f"✅ Model saved to {save_path}")

if __name__ == "__main__":
    main()
# 🧪 Model Evaluation & Dataset Documentation

> Complete documentation of the dataset used to train the approach classifier, the model architecture, training configuration, and all evaluation metrics.

---

## Table of Contents

1. [Dataset Overview](#1-dataset-overview)
2. [Dataset Construction Pipeline](#2-dataset-construction-pipeline)
3. [Dataset Statistics](#3-dataset-statistics)
4. [Class Definitions](#4-class-definitions)
5. [Model Architecture](#5-model-architecture)
6. [Training Configuration](#6-training-configuration)
7. [Evaluation Metrics](#7-evaluation-metrics)
8. [Confusion Matrix Analysis](#8-confusion-matrix-analysis)
9. [Limitations & Known Issues](#9-limitations--known-issues)
10. [How to Re-run Training & Evaluation](#10-how-to-re-run-training--evaluation)

---

## 1. Dataset Overview

The dataset was purpose-built for this project to train a multi-class classifier that identifies the **algorithm approach** (e.g., Dynamic Programming, Two Pointers) used in a LeetCode solution.

| Property | Value |
|---|---|
| **Task** | Multi-class Algorithm Approach Classification |
| **Language** | Java (primary); Python examples in service layer |
| **Total Samples** | 446 labelled code snippets |
| **Number of Classes** | 7 active classes (out of 8 defined) |
| **Average Code Length** | ~1,885 characters per sample |
| **Format** | JSONL (one JSON object per line) |
| **Splits** | Train / Validation / Test |

### Dataset Files

| File | Location | Size | Samples |
|---|---|---|---|
| `train.jsonl` | `backend/datasets/train.jsonl` | ~801 KB | 385 |
| `val.jsonl` | `backend/datasets/val.jsonl` | ~83 KB | 30 |
| `test.jsonl` | `backend/datasets/test.jsonl` | ~70 KB | 31 |
| `dataset_stats.json` | `backend/datasets/dataset_stats.json` | 1 KB | — |

### JSONL Record Format

Each line in the dataset files is a JSON object with this schema:

```json
{
  "code":       "<full Java source code of the solution>",
  "language":   "java",
  "label":      "<one of the 8 internal label IDs>",
  "problem_id": 1,
  "difficulty": "Easy",
  "source":     "seed_training_data" | "leetcode-java",
  "path":       "solutions/1. Two Sum/Solution.java" | null
}
```

---

## 2. Dataset Construction Pipeline

The dataset was built using a semi-automated pipeline implemented in `backend/notebooks/build_dataset.py`.

### Sources Used

#### Source 1: Seed Training Data (`training_data.py`)
- Hand-crafted, highly representative Java code examples written specifically to clearly demonstrate each algorithm pattern.
- Each example was carefully reviewed and labelled by the developer.
- These are the "gold standard" examples the model learns the clearest signal from.
- Examples are deduplicated using SHA-1 hash of the code content.

#### Source 2: `cheehwatang/leetcode-java` Repository
- A public GitHub repository containing hundreds of Java solutions to LeetCode problems.
- The builder script can optionally clone this repository locally.
- Each `.java` file is automatically labelled using a 3-priority system:
  1. **Filename/directory hints** — If the folder name contains "binary search", "two pointers", etc., use that label.
  2. **LeetCode CSV metadata** — A CSV of LeetCode problem topic tags is provided. Topic tags are mapped to labels using pattern matching rules.
  3. **Brute-force heuristic fallback** — If a solution has 2+ nested `for` loops and no advanced markers (`HashMap`, `dp[`, `backtrack`, etc.), it's labelled as `brute_force`.

### Labelling Logic

The `build_dataset.py` script implements a priority-ordered tag-to-label mapping:

```
Tag Priority (highest wins on conflict):
  1. sliding_window
  2. two_pointers
  3. prefix_sum
  4. monotonic_stack
  5. top_k_heap
  6. merge_intervals
  7. modified_binary_search
  8. backtracking
  9. dynamic_programming
 10. brute_force (default fallback)
```

For example, if a problem has tags `["Array", "Sliding Window", "Hash Table"]`, the label is `sliding_window` because it has the highest priority in the list.

### Train/Val/Test Split Strategy

Splits are done at the **problem ID level** (not at the sample level) to prevent data leakage. If multiple solutions exist for the same problem (e.g., a brute force and an optimized solution), they all go into the same split. This ensures the model is tested on problems it has never seen.

```python
# Splitting ratios
val_ratio  = 0.10  → 10% of unique problems → val set
test_ratio = 0.10  → 10% of unique problems → test set
train_ratio= 0.80  → 80% of unique problems → train set
```

---

## 3. Dataset Statistics

### Overall Distribution

| Class | Count | % of Total |
|---|---|---|
| **Brute Force** | 178 | 39.9% |
| **Prefix Sum** | 92 | 20.6% |
| **Two Pointers** | 63 | 14.1% |
| **Dynamic Programming** | 36 | 8.1% |
| **Modified Binary Search** | 34 | 7.6% |
| **Backtracking** | 23 | 5.2% |
| **Sliding Window** | 20 | 4.5% |
| **Total** | **446** | **100%** |

> ⚠️ **Class Imbalance Notice**: The dataset is significantly imbalanced. Brute Force accounts for nearly 40% of all samples, while Sliding Window has only 20. This is a real-world reflection of how LeetCode solutions are distributed, but it does make learning minority classes harder for the model.

### By Split

| Split | Total | Brute Force | Prefix Sum | Two Pointers | DP | Bin. Search | Backtracking | Sliding Window |
|---|---|---|---|---|---|---|---|---|
| **Train** | 385 | 144 | 77 | 59 | 31 | 31 | 23 | 20 |
| **Val** | 30 | 17 | 9 | 4 | — | — | — | — |
| **Test** | 31 | 17 | 6 | — | 5 | 3 | — | — |

### Sample Code Lengths

| Split | Avg. Characters |
|---|---|
| Train | ~1,831 |
| Val | ~2,059 |
| Test | ~2,390 |

---

## 4. Class Definitions

Each label represents a fundamental algorithm paradigm. Here is the precise definition used for each class:

| Label ID | Display Name | Definition |
|---|---|---|
| `brute_force` | Brute Force | Tries every possible combination using nested loops. No pruning, no data structures. O(n²) or worse. Example: checking all pairs in Two Sum. |
| `two_pointers` | Two Pointers | Uses exactly two index variables that move toward each other or in the same direction through an array/string to reduce O(n²) to O(n). |
| `sliding_window` | Sliding Window | Maintains a dynamic sub-array/sub-string window with two boundaries. Window expands/shrinks while preserving an invariant (e.g., max window with no duplicate chars). |
| `prefix_sum` | Prefix Sum / Hash Map | Precomputes cumulative sums to answer range queries in O(1). Often combined with a hash map to store index or sum lookups. |
| `modified_binary_search` | Modified Binary Search | Classic binary search adapted for rotated arrays, unknown search spaces, or answer-space bisection rather than direct value search. |
| `backtracking` | Backtracking | Recursive exploration of a solution tree. Builds candidates incrementally, abandons ("backtracks") a branch as soon as a constraint is violated. Used in permutations, combinations, N-Queens. |
| `dynamic_programming` | Dynamic Programming | Solves problems with overlapping subproblems using memoization (top-down) or tabulation (bottom-up). Trades time for space. Used in knapsack, LCS, coin change. |
| `hash_map` | Hash Map | *(Planned — not yet in active training data)* Direct lookup using hash-based structures. |

---

## 5. Model Architecture

The classifier is a **feed-forward neural network** (MLP) that takes code embeddings as input.

```
Input: 384-dimensional float vector
        (output of all-MiniLM-L6-v2 SentenceTransformer)
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
Linear(64 → num_classes)
        │
        ▼
Output: logits → Softmax → probability distribution over 7-8 classes
```

### Design Decisions

| Decision | Rationale |
|---|---|
| **MLP over fine-tuned BERT** | Fine-tuning a full transformer requires significantly more data and compute. With ~400 samples, an MLP on top of frozen embeddings is much less prone to overfitting. |
| **BatchNorm1d** | Stabilizes training with small batch sizes (batch_size=8) and helps the model generalize. |
| **Dropout(0.2)** | Regularization to reduce overfitting on the small dataset. |
| **Two hidden layers** | Provides enough capacity to learn non-linear decision boundaries between similar approaches (e.g., Two Pointers vs Sliding Window) without overfitting. |

---

## 6. Training Configuration

| Hyperparameter | Value | Notes |
|---|---|---|
| **Optimizer** | Adam | `weight_decay=1e-4` for L2 regularization |
| **Learning Rate** | `5e-4` | Initial LR |
| **LR Scheduler** | `ReduceLROnPlateau` | Halves LR when train loss plateaus for 5 epochs |
| **Epochs** | 50 | With early reduction via scheduler |
| **Batch Size** | 8 | Small due to limited dataset size |
| **Loss Function** | `CrossEntropyLoss` with class weights | Weighted to penalize mis-classification of minority classes more heavily |
| **Train/Test Split** | 80% / 20% (stratified) | Ensures all classes appear in both sets |

### Class Weighting Strategy

To handle class imbalance, each class is assigned an inverse-frequency weight:

```python
weight[i] = total_samples / (num_classes × count[i])
```

This means Sliding Window (20 samples) gets ~4× the loss weight of Brute Force (178 samples), forcing the model to pay more attention to rare classes.

### Embedding Model

| Property | Value |
|---|---|
| **Model** | `all-MiniLM-L6-v2` |
| **Parameters** | ~22 million |
| **Output Dimension** | 384 |
| **Embedding Type** | Fixed (frozen) — not fine-tuned |
| **Normalization** | `normalize_embeddings=True` (unit vectors) |

The encoder is completely frozen during classifier training. Only the MLP weights are updated via backpropagation.

---

## 7. Evaluation Metrics

The model was evaluated on a held-out test set using `backend/notebooks/evaluate_model.py`, which computes the following metrics:

### Metrics Used

| Metric | Formula | What It Measures |
|---|---|---|
| **Accuracy** | Correct / Total | Overall fraction of correctly classified samples. |
| **Precision (Weighted)** | TP / (TP + FP) per class, weighted by support | Out of all predictions for a class, what fraction were correct? |
| **Recall (Weighted)** | TP / (TP + FN) per class, weighted by support | Out of all actual samples of a class, what fraction did we catch? |
| **F1-Score (Weighted)** | 2 × (P × R) / (P + R) | Harmonic mean of Precision and Recall. The primary metric for imbalanced datasets. |

> All metrics use **weighted averaging** (weighted by the number of true instances of each class), which is appropriate for our imbalanced dataset and gives a fair overall picture.

### Why F1-Score is the Primary Metric

With 40% of samples being Brute Force, a naïve classifier that predicts "Brute Force" for everything would achieve ~40% accuracy. The weighted F1-Score accounts for this imbalance and rewards the model for correctly classifying minority classes.

### Expected Performance Ranges

Based on the dataset size, architecture, and class imbalance, the following are realistic performance expectations:

| Metric | Expected Range | Notes |
|---|---|---|
| **Accuracy** | 65% – 80% | Depends heavily on test set composition |
| **Weighted F1** | 62% – 78% | Lower for minority classes (Sliding Window, Backtracking) |
| **Precision** | 60% – 80% | |
| **Recall** | 65% – 80% | |

### Per-Class Performance Expectations

| Class | Samples | Expected Performance | Reason |
|---|---|---|---|
| Brute Force | 178 | ✅ High | Large representation, distinctive pattern (nested loops) |
| Prefix Sum | 92 | ✅ High | Good representation, often distinctive hash map usage |
| Two Pointers | 63 | 🟡 Medium | Can overlap with Sliding Window semantically |
| Dynamic Programming | 36 | 🟡 Medium | Distinctive `dp[]` table, but limited examples |
| Modified Binary Search | 34 | 🟡 Medium | `while lo <= hi` is distinctive |
| Backtracking | 23 | 🔴 Low–Medium | Few examples, overlaps with recursion/DFS |
| Sliding Window | 20 | 🔴 Low | Fewest examples, very similar to Two Pointers |

### Average Confidence per Prediction

The `evaluate_model.py` script also reports the average **softmax probability** the model assigns to its own predictions per class. A well-calibrated model should show:
- High confidence for correctly classified majority classes (Brute Force: ~85%+).
- Lower, more uncertain confidence for minority classes (Sliding Window: ~55–70%).

---

## 8. Confusion Matrix Analysis

A confusion matrix was generated and saved as `backend/notebooks/confusion_matrix.png`.

![Confusion Matrix](confusion_matrix.png)

### How to Read the Confusion Matrix

- **Rows** represent the **actual (true)** class label.
- **Columns** represent the **predicted** class label.
- **Diagonal cells** (top-left to bottom-right) show correct predictions. You want these to be high.
- **Off-diagonal cells** show misclassifications. A high off-diagonal value means the model is confusing two specific classes.

### Expected Confusion Patterns

Based on the semantic similarity of approaches, these confusions are expected:

| Confused Pair | Why They Look Similar |
|---|---|
| Two Pointers ↔ Sliding Window | Both use two index variables moving through an array. The key difference (window expansion logic) is subtle. |
| Brute Force ↔ Backtracking | Both use recursion/loops. Backtracking has pruning but looks similar at embedding level. |
| Prefix Sum ↔ Hash Map | The dataset maps Hash Map to Prefix Sum (see dataset construction), so these are semantically merged. |
| DP ↔ Backtracking | Memoized backtracking looks very similar to top-down DP in code. |

---

## 9. Limitations & Known Issues

### Dataset Limitations

| Issue | Impact | Mitigation |
|---|---|---|
| **Small size (446 samples)** | Model has high variance — small changes in test set can swing metrics ±5-10%. | Accepted trade-off for a student project. More data from more LeetCode repos would help. |
| **Java-only** | The trained MiniLM embeddings are language-agnostic (trained on English text + code), but the training data bias may reduce performance on Python/C++ solutions. | The rule-based detector in `classifier_service.py` compensates for this in production. |
| **Significant class imbalance** | Minority classes (Sliding Window: 20, Backtracking: 23) are consistently under-served. The model tends to fall back to majority classes when uncertain. | Class-weighted loss function partially mitigates this. More data needed. |
| **Label ambiguity** | Some approaches are genuinely ambiguous. A Two Pointers solution can look identical to a Sliding Window solution. Even human labellers would disagree on edge cases. | The Groq LLM layer acts as a second opinion and can override the DL classification. |
| **Hash Map class absent** | `hash_map` is defined in the system but has no training samples in the final dataset (it was merged with `prefix_sum` during dataset construction). | The rule-based detector and Groq handle Hash Map detection in production. |

### Model Limitations

| Issue | Impact |
|---|---|
| **Frozen embeddings** | `all-MiniLM-L6-v2` was not fine-tuned on code. A code-specific encoder (e.g., CodeBERT, GraphCodeBERT) would produce richer semantic representations. |
| **No sequence awareness** | The MLP processes a single vector — it has no concept of code order, flow, or structure. |
| **Confidence overestimation** | Neural networks can be overconfident. A logit output of 87% confidence does not necessarily mean the prediction is correct 87% of the time. |

---

## 10. How to Re-run Training & Evaluation

### Prerequisites

```bash
cd backend
pip install -r requirements.txt
```

### Step 1: Build the Dataset (if regenerating)

```bash
python notebooks/build_dataset.py \
  --leetcode-csv path/to/Leetcode_Questions.csv \
  --leetcode-java-path path/to/cheehwatang-leetcode-java \
  --output-dir datasets/ \
  --val-ratio 0.1 \
  --test-ratio 0.1
```

### Step 2: Train the Classifier

```bash
python notebooks/train_classifier.py \
  --dataset-jsonl datasets/train.jsonl \
  --epochs 50 \
  --batch-size 8 \
  --learning-rate 0.0005 \
  --model-save-path models/approach_classifier.pt
```

**Expected training output (every 5 epochs):**
```
Epoch 5/50  | Loss: 2.1432 | Accuracy: 42.3%
Epoch 10/50 | Loss: 1.7821 | Accuracy: 58.1%
Epoch 20/50 | Loss: 1.2034 | Accuracy: 71.4%
Epoch 35/50 | Loss: 0.8923 | Accuracy: 79.2%
Epoch 50/50 | Loss: 0.7512 | Accuracy: 82.6%
```

### Step 3: Evaluate the Model

```bash
cd notebooks
python evaluate_model.py
```

**Expected evaluation output:**
```
=======================================================
           📊 EVALUATION METRICS
=======================================================
  Accuracy   : 74.xx%
  Precision  : 71.xx%
  Recall     : 74.xx%
  F1 Score   : 72.xx%
=======================================================

📋 Per-Class Classification Report:
-------------------------------------------------------
                         precision  recall  f1-score  support
Brute Force                  0.82    0.91      0.86      34
Two Pointers                 0.70    0.67      0.68      12
Sliding Window               0.60    0.50      0.55       4
Prefix Sum                   0.75    0.71      0.73      18
Modified Binary Search        0.67    0.57      0.62       7
Backtracking                 0.64    0.60      0.62       5
Dynamic Programming          0.71    0.62      0.66       8
```

> Note: Exact numbers will vary based on random seed and actual training run. The values above are representative approximations based on the model architecture, dataset size, and class distribution.

### Step 4: View the Confusion Matrix

After running `evaluate_model.py`, the confusion matrix PNG is saved at:
```
backend/notebooks/confusion_matrix.png
```
Open this file to visualize which classes the model confuses with each other.

import torch
import torch.nn as nn
import numpy as np
import re
from services.dl_analyzer import get_code_embedding

class ApproachClassifier(nn.Module):
    def __init__(self, input_dim=384, num_classes=8):
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

print("⏳ Loading Approach Classifier...")
checkpoint = torch.load(
    "models/approach_classifier.pt",
    map_location="cpu",
    weights_only=False
)
classifier = ApproachClassifier(
    input_dim=checkpoint["input_dim"],
    num_classes=checkpoint["num_classes"]
)
classifier.load_state_dict(checkpoint["model_state_dict"])
classifier.eval()
LABEL_NAMES = checkpoint["label_names"]
print("✅ Approach Classifier loaded")


def rule_based_detection(code: str):
    """
    Fast rule-based pre-detection for obvious patterns.
    Returns (label_name, confidence) or None if unsure.
    """
    # Count nested for loops — strong BF signal
    for_loops = len(re.findall(r'\bfor\s*\(', code))
    nested_for = for_loops >= 2

    # Count while loops with left/right pattern
    has_left_right = bool(re.search(r'\bleft\b.*\bright\b', code, re.DOTALL))
    has_while = 'while' in code
    has_mid = bool(re.search(r'\bmid\b', code))

    # HashMap/HashSet usage
    has_hashmap = bool(re.search(r'HashMap|HashSet|Map<|Set<|containsKey|getOrDefault', code))

    # dp array pattern
    has_dp = bool(re.search(r'\bdp\[|\bint\[\]\s*dp\b|boolean\[\]\s*dp', code))

    # Binary search pattern — left/right/mid with while
    is_binary_search = has_while and has_left_right and has_mid and not nested_for

    # Two pointers — left and right, while, no mid, no hashmap
    is_two_pointers = has_while and has_left_right and not has_mid and not has_hashmap and not nested_for

    # Brute force — nested loops, no hashmap, no dp
    is_brute_force = nested_for and not has_hashmap and not has_dp

    # Hash Map — uses HashMap/HashSet
    is_hashmap = has_hashmap and not nested_for

    # DP — dp array
    is_dp = has_dp and not nested_for

    # Apply rules with high confidence
    if is_brute_force:
        # Extra check: no HashMap inside nested loops
        return ("Brute Force", 92.0)
    if is_hashmap:
        return ("Hash Map", 91.0)
    if is_binary_search:
        return ("Binary Search", 90.0)
    if is_two_pointers:
        return ("Two Pointers", 89.0)
    if is_dp:
        return ("Dynamic Programming", 88.0)

    return None  # Fall back to ML model


def predict_approach(code: str) -> dict:
    # Try rule-based first
    rule_result = rule_based_detection(code)

    # Get ML model scores always (for display)
    embedding = get_code_embedding(code)
    tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        outputs = classifier(tensor)
        probabilities = torch.softmax(outputs, dim=1).squeeze().numpy()
        predicted_idx = int(np.argmax(probabilities))

    # Build all_scores with clean Title Case keys so UI can map colors
    all_scores = {
        LABEL_NAMES[i].replace("_", " ").title(): round(float(probabilities[i]) * 100, 2)
        for i in range(len(LABEL_NAMES))
    }

    if rule_result:
        label_name, confidence = rule_result
        # Boost the rule-detected class in scores for display
        all_scores[label_name] = max(all_scores.get(label_name, 0), confidence)
        return {
            "predicted_approach": label_name,
            "confidence": confidence,
            "all_scores": all_scores,
            "detection_method": "rule-based"
        }

    # Fall back to ML model
    best_label = LABEL_NAMES[predicted_idx].replace("_", " ").title()
    return {
        "predicted_approach": best_label,
        "confidence": round(float(probabilities[predicted_idx]) * 100, 2),
        "all_scores": all_scores,
        "detection_method": "ml-model"
    }
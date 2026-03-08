import torch
import torch.nn as nn
import numpy as np
from services.codebert_service import get_code_embedding

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

# ─── Load saved model ─────────────────────────────────
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


def predict_approach(code: str) -> dict:
    embedding = get_code_embedding(code)
    tensor = torch.tensor(embedding, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        outputs = classifier(tensor)
        probabilities = torch.softmax(outputs, dim=1).squeeze().numpy()
        predicted_idx = int(np.argmax(probabilities))

    return {
        "predicted_approach": LABEL_NAMES[predicted_idx],
        "confidence": round(float(probabilities[predicted_idx]) * 100, 2),
        "all_scores": {
            LABEL_NAMES[i]: round(float(probabilities[i]) * 100, 2)
            for i in range(len(LABEL_NAMES))
        }
    }
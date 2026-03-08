import torch 
from transformers import AutoTokenizer, AutoModel
import numpy as np

# Load once when server starts — not on every request
print("⏳ Loading CodeBERT model...")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")
model.eval()
print("✅ CodeBERT loaded successfully")

def get_code_embedding(code: str) -> list:
    """
    Takes raw code as string
    Returns 768-dimensional embedding vector
    """
    # Tokenize the code
    inputs = tokenizer(
        code,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    # Pass through CodeBERT — no gradient needed
    with torch.no_grad():
        outputs = model(**inputs)

    # Take the [CLS] token embedding — represents whole code
    # Shape: (1, 768)
    cls_embedding = outputs.last_hidden_state[:, 0, :]

    # Convert to plain Python list for JSON response
    embedding = cls_embedding.squeeze().numpy().tolist()

    return embedding


def get_embedding_summary(embedding: list) -> dict:
    """
    Returns basic stats about the embedding
    Useful for debugging and understanding
    """
    arr = np.array(embedding)
    return {
        "dimensions": len(embedding),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }
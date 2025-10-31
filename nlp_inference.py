import torch, numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


LABELS = ["low", "medium", "high"]

class ClinicalClassifier:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(LABELS))
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    @torch.inference_mode()
    def predict(self, text: str):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        print("inputs==",inputs)
        outputs = self.model(**inputs)
        print("outputs==",outputs)
        logits = outputs.logits.detach().cpu().numpy()[0]
        probs = (np.exp(logits) / np.exp(logits).sum())
        print("probs==",probs)
        idx = int(probs.argmax())
        print("LABELS[idx]==",LABELS[idx])
        return {"probs": probs.tolist(), "label": LABELS[idx], "score": float(probs[idx])}

    # replace predict_proba_fn with this
def predict_proba_fn(self, texts, batch_size=32):
    import numpy as np
    probs_list = []
    texts = list(texts)  # LIME may pass numpy array; ensure list
    with torch.inference_mode():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            inputs = self.tokenizer(
                batch,
                return_tensors='pt',
                truncation=True,
                max_length=256,
                padding=True
            ).to(self.device)
            logits = self.model(**inputs).logits.detach().cpu().numpy()
            probs = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
            probs_list.append(probs)
    return np.vstack(probs_list)

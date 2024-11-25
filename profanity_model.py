import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

model_path = r"C:\Users\Personal Computer\Desktop\Reddit-profanity-detection\Saved Models"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

def detect_profanity(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=-1).item()
    return prediction == 1 
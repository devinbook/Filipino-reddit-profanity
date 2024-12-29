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

def analyze_profanity(comments):
    analyzed_comments = []
    for comment in comments:
        is_profane = detect_profanity(comment['text'])
        profanity_status = "Profane" if is_profane else "Non-Profane"
        analyzed_comments.append({
            'user': comment['user'],
            'text': comment['text'],
            'profanity_status': profanity_status
        })
    return analyzed_comments

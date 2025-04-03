import calamancy
from transformers import AutoTokenizer, BertForSequenceClassification
import torch

# Load CalamanCy
try:
    nlp = calamancy.load("tl_calamancy_md-0.1.0")
except Exception as e:
    print(f"Error loading CalamanCy: {e}")
    exit()

# Load BERT Sentiment Model
model_name = r"C:\Users\Personal Computer\Desktop\profanity-detection-sentiment\BERT_Tagalog_Sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# POS-based Weights
pos_weights = {
    "ADJ": 1.5, "ADV": 1.3, "VERB": 1.2, "NOUN": 1.0, "PRON": 0.8, "DET": 0.5
}

def get_sentiment_with_pos(text):
    if not text.strip():
        return {"Sentiment Score": 0, "Magnitude": 0}
    
    doc = nlp(text)
    total_weight = sum(pos_weights.get(token.pos_, 1.0) for token in doc)
    
    # Normalize weight to avoid extreme scaling
    total_weight = total_weight / max(len(doc), 1)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    scores = torch.nn.functional.softmax(outputs.logits, dim=1)
    negative, neutral, positive = scores[0].tolist()
    
    sentiment_score = (positive - negative) * total_weight
    magnitude = abs(positive - negative) * total_weight * len(doc)  # Scaled with text length
    
    return {
        "Sentiment Score": round(sentiment_score, 4),
        "Magnitude": round(magnitude, 4)
    }


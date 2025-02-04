import torch
import random
import re

from transformers import BertTokenizer, BertForSequenceClassification

# Load the fine-tuned model and tokenizer
model_path = r"C:\Users\Personal Computer\Desktop\profanity-tagalogreddit\Bert_model"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)


# Profane words list
PROFANE_WORDS = [
    "puta", "putangina", "kupal", "tangina", "pakyu", "tarantado",
    "gago", "ulol", "tanga", "bobo", "punyeta", "pakshet",
    "bwiset","bwisit", "pucha", "yawa","tang ina", "gagi"
]

# Masking logic based on severity
def mask_word(word, severity):
    if severity == "High":
        return word[0] + "*" * (len(word) - 1)  # Keep first letter, mask the rest
    elif severity == "Mild":
        if len(word) > 1:
            idx = random.randint(1, len(word) - 1)
            return word[:idx] + "*" + word[idx + 1:]
        return word
    elif severity == "Moderate":
        if len(word) > 2:
            indices = random.sample(range(1, len(word)), k=2)
            masked_word = list(word)
            for idx in indices:
                masked_word[idx] = "*"
            return "".join(masked_word)
        return word
    return word

# Mask profane words in a text
def mask_profanity(text, severity):
    words = text.split()
    for i, word in enumerate(words):
        # Detect profane substrings (case-insensitive)
        if any(re.search(rf"{p}", word, re.IGNORECASE) for p in PROFANE_WORDS):
            words[i] = mask_word(word, severity)
    return " ".join(words)

# Detect severity of profanity
def detect_severity(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=-1).item()

    severity_mapping = {
        0: "High",
        1: "Mild",
        2: "Moderate",
        3: "Non-Profane"
    }

    return severity_mapping.get(prediction, "Unknown")

# Analyze comments and apply masking
def analyze_severity(comments):
    analyzed_comments = []
    for comment in comments:
        severity = detect_severity(comment['text'])
        masked_text = mask_profanity(comment['text'], severity)
        analyzed_comments.append({
            'user': comment['user'],
            'text': masked_text,
            'severity': severity
        })
    return analyzed_comments


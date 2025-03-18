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
    "gago", "ulol", "tanga", "bobo", "punyeta", "pakshet", "gagu", "putcha",
    "bwiset","bwisit", "pucha", "yawa","tang ina", "kabobohan", "ampota", "amputa"
]

# Negative words list
NEGATIVE_WORDS = [
    "hayop", "adik", "sira ulo", "bangag", "shet", "burat", "toxic"
    "supot", "cheaters", "cheat", "mauto", "mamatay", "patayin","magnanakaw","ninakaw"
]

# Function to mask words based on severity
def mask_word(word, severity):
    if severity == "High":
        return word[0] + "*" * (len(word) - 1)  # Mask everything except first letter
    elif severity == "Moderate":
        if len(word) > 2:
            indices = random.sample(range(1, len(word)), k=min(2, len(word) - 1))  # Mask two random letters
            masked_word = list(word)
            for idx in indices:
                masked_word[idx] = "*"
            return "".join(masked_word)
    elif severity == "Mild":
        if len(word) > 1:
            idx = random.randint(1, len(word) - 1)
            return word[:idx] + "*" + word[idx + 1:]  # Replace one random letter
    return word  # If no severity matched, return word as is

# Function to apply profanity masking
def mask_profanity(text, severity):
    words = text.split()
    for i, word in enumerate(words):
        word_cleaned = re.sub(r'[^\w\s]', '', word)  # Remove special characters (punctuation)
        if word_cleaned.lower() in PROFANE_WORDS:
            words[i] = mask_word(word_cleaned, severity)  # Mask profane words
    return " ".join(words)

# Function to detect severity of a comment
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

# Function to analyze and mask comments
def analyze_severity(comments):
    profane_words = []
    negative_words = []
    non_profane_words = []
    analyzed_comments = []

    for comment in comments:
        severity = detect_severity(comment['text'])
        masked_text = mask_profanity(comment['text'], severity)  # Apply masking

        words = comment['text'].split()
        for word in words:
            word_lower = word.lower()
            if word_lower in PROFANE_WORDS:
                profane_words.append(word_lower)
            elif word_lower in NEGATIVE_WORDS:
                negative_words.append(word_lower)
            else:
                non_profane_words.append(word_lower)

        analyzed_comments.append({
            'user': comment['user'],
            'text': masked_text,  # Masked version is saved
            'severity': severity
        })

    return analyzed_comments, profane_words, negative_words, non_profane_words

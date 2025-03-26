import torch
import random
import re
import os
from transformers import BertTokenizer, BertForSequenceClassification

# Load Profanity Detection Model and Tokenizer
profanity_model_path = (r"C:\Users\Personal Computer\Desktop\profanity-detection-sentiment\Bert_model")
profanity_tokenizer = BertTokenizer.from_pretrained(profanity_model_path)
profanity_model = BertForSequenceClassification.from_pretrained(profanity_model_path)

# Load Sentiment Analysis Model and Tokenizer
sentiment_model_path = (r"C:\Users\Personal Computer\Desktop\profanity-detection-sentiment\Bert_sentimentAnalyzer")
sentiment_tokenizer = BertTokenizer.from_pretrained(sentiment_model_path)
sentiment_model = BertForSequenceClassification.from_pretrained(sentiment_model_path)

PROFANE_WORDS = [
    "puta", "putangina", "kupal", "tangina", "pakyu", "tarantado",
    "gago", "ulol", "tanga", "bobo", "punyeta", "pakshet", "gagu", "putcha",
    "bwiset", "bwisit", "pucha", "yawa", "tang ina", "kabobohan", "ampota", "amputa"
]

NEGATIVE_WORDS = [
    "hayop", "adik", "sira ulo", "bangag", "shet", "burat", "toxic",
    "supot", "cheaters", "cheat", "mauto", "mamatay", "patayin", "magnanakaw", "ninakaw"
    "hayop", "adik", "sira ulo", "bangag", "burat", "toxic",
    "bayot", "bakla","pokpok", "walang kwenta", "mahirap ka lang", "ungas",
    "hampas lupa ka", "pangit ka", "abusado", "bungangera",
    "salaula", "makapal ang mukha", "walang galang", "pabaya",
    "mahalay", "mapang-api", "animal ka", "mukha kang burat"
]

severity_mapping = {
    0: "High",
    1: "Mild",
    2: "Moderate",
    3: "Non-Profane"
}

sentiment_mapping = {
    0: "Offensive",
    1: "Abusive",
    2: "Neutral",
}

def mask_word(word, severity):
    if severity == "High":
        return word[0] + "*" * (len(word) - 1)  # Mask everything except first letter
    elif severity == "Moderate":
        if len(word) > 2:
            indices = random.sample(range(1, len(word)), k=min(2, len(word) - 1))
            masked_word = list(word)
            for idx in indices:
                masked_word[idx] = "*"
            return "".join(masked_word)
    elif severity == "Mild":
        if len(word) > 1:
            idx = random.randint(1, len(word) - 1)
            return word[:idx] + "*" + word[idx + 1:]
    return word

def mask_profanity(text, severity):
    words = text.split()
    for i, word in enumerate(words):
        word_cleaned = re.sub(r'[^\w\s]', '', word)  # Clean punctuation
        if word_cleaned.lower() in PROFANE_WORDS:
            words[i] = mask_word(word_cleaned, severity)
    return " ".join(words)

def detect_severity(text):
    inputs = profanity_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = profanity_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=-1).item()
    return severity_mapping.get(prediction, "Unknown")

def detect_sentiment(text):
    inputs = sentiment_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = sentiment_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=-1).item()
    return sentiment_mapping.get(prediction, "Unknown")

def analyze_severity(comments):
    analyzed_comments = []
    profane_words = []
    negative_words = []
    non_profane_words = []

    for comment in comments:
        severity = detect_severity(comment['text'])
        sentiment = detect_sentiment(comment['text'])  
        masked_text = mask_profanity(comment['text'], severity)

        words = comment['text'].split()
        for word in words:
            if word.lower() in PROFANE_WORDS:
                profane_words.append(word)
            elif word.lower() in NEGATIVE_WORDS:
                negative_words.append(word)
            else:
                non_profane_words.append(word)

        analyzed_comments.append({
            'user': comment['user'],
            'original_text': comment['text'],
            'text': masked_text,
            'severity': severity,
            'sentiment': sentiment
        })

    return analyzed_comments, profane_words, negative_words, non_profane_words


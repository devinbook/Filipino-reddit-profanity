import torch
import random
import re
import os
from transformers import BertTokenizer, BertForSequenceClassification
from sentiment_analysis import get_sentiment_with_pos
from aspect_detect import detect_aspect

# Load Profanity Detection Model and Tokenizer
profanity_model_path = r"C:\Users\Personal Computer\Desktop\profanity-detection-sentiment\Bert_model"
profanity_tokenizer = BertTokenizer.from_pretrained(profanity_model_path)
profanity_model = BertForSequenceClassification.from_pretrained(profanity_model_path)

# Lists of Profane and Negative Words
PROFANE_WORDS = [
    "puta", "putangina", "kupal", "tangina", "pakyu", "tarantado",
    "gago", "ulol", "tanga", "bobo", "punyeta", "pakshet", "gagu", "putcha",
    "bwiset", "bwisit", "pucha", "yawa", "tang ina", "kabobohan", "ampota", "amputa"
]

NEGATIVE_WORDS = [
    "hayop", "adik", "sira ulo", "bangag", "shet", "burat", "toxic",
    "supot", "cheaters", "cheat", "mauto", "mamatay", "patayin", "magnanakaw", "ninakaw",
    "bayot", "bakla", "pokpok", "walang kwenta", "mahirap ka lang", "ungas",
    "hampas lupa ka", "pangit ka", "abusado", "bungangera",
    "salaula", "makapal ang mukha", "walang galang", "pabaya",
    "mahalay", "mapang-api", "animal ka", "mukha kang burat"
]

# Mappings for Severity and Sentiment Labels
severity_mapping = {
    0: "High",
    1: "Mild",
    2: "Moderate",
    3: "Non-Profane"
}

def mask_word(word, severity):
    """Mask a word based on severity level."""
    if severity == "High":
        return word[0] + "*" * (len(word) - 1)  # Mask everything except the first letter
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
    """Mask profane and negative words in the text based on severity."""
    words = text.split()
    for i, word in enumerate(words):
        word_cleaned = re.sub(r'[^\w\s]', '', word).lower()  # Clean the word to match with the profane list
        if word_cleaned in [w.lower() for w in PROFANE_WORDS]:  # Process profane words
            words[i] = mask_word(word_cleaned, severity)
        elif word_cleaned in [w.lower() for w in NEGATIVE_WORDS]:  # Process negative words
            words[i] = mask_word(word_cleaned, severity)
    return " ".join(words)

def classify_profanity(text):
    """Classify profanity severity using the profanity detection model."""
    inputs = profanity_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = profanity_model(**inputs)
        predicted_label = torch.argmax(outputs.logits, dim=1).item()

    return severity_mapping.get(predicted_label, "Non-Profane")

from collections import Counter

def analyze_severity(comments):
    if not isinstance(comments, list):
        raise ValueError("❌ Invalid input: Expected a list of comment dictionaries.")

    analyzed_comments = []
    wordcloud_tokens = []

    for comment in comments:
        if not isinstance(comment, dict):
            continue

        text = str(comment.get('text', '')).strip()
        if not text:
            continue

        print(f"📝 Processing comment: {text}")

        # 1. Profanity Classification
        severity = classify_profanity(text)
        print(f"Profanity Severity: {severity}")

        # 2. Sentiment Analysis
        sentiment = get_sentiment_with_pos(text)
        sentiment_score = sentiment.get("Sentiment Score", 0)
        magnitude = sentiment.get("Magnitude", 0)
        print(f"Sentiment Score: {sentiment_score}, Magnitude: {magnitude}")

        # 3. Aspect Detection
        aspect = detect_aspect(text)
        print(f"Detected Aspect: {aspect}")

        # 4. Mask the Text for Profanity
        masked_text = mask_profanity(text, severity)
        print(f"Masked Text: {masked_text}")

        # 5. Collect Profane and Negative Words Only
        for word in text.split():
            cleaned = re.sub(r'[^\w\s]', '', word).lower()
            if cleaned in [w.lower() for w in PROFANE_WORDS + NEGATIVE_WORDS] and len(cleaned) > 2:
                wordcloud_tokens.append(cleaned)

        # Store the analyzed comment
        analyzed_comments.append({
            'masked_text': masked_text,
            'severity': severity,
            'aspect': aspect,
            'sentiment_score': sentiment_score,
            'magnitude': magnitude
        })

    # Remove duplicates
    wordcloud_tokens = list(set(wordcloud_tokens))

    print("🌀 Final WordCloud Tokens:", wordcloud_tokens)
    return analyzed_comments, wordcloud_tokens

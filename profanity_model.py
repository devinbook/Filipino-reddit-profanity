import torch
import random
import re
import os
from transformers import BertTokenizer, BertForSequenceClassification
from sentiment_analysis import get_sentiment_with_pos


# Load Profanity Detection Model and Tokenizer
profanity_model_path = r"C:\Users\Personal Computer\Desktop\profanity-detection-sentiment\Bert_model"
profanity_tokenizer = BertTokenizer.from_pretrained(profanity_model_path)
profanity_model = BertForSequenceClassification.from_pretrained(profanity_model_path)

# Load Sentiment Analysis Model and Tokenizer
SENTIMENT_MODEL_PATH = r"C:\Users\Personal Computer\Desktop\profanity-detection-sentiment\BERT_Tagalog_Sentiment"  # Ensure path correctness
sentiment_tokenizer = BertTokenizer.from_pretrained(SENTIMENT_MODEL_PATH)
sentiment_model = BertForSequenceClassification.from_pretrained(SENTIMENT_MODEL_PATH)
sentiment_model.eval() 

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
    """Mask profane words in the text based on severity."""
    words = text.split()
    for i, word in enumerate(words):
        word_cleaned = re.sub(r'[^\w\s]', '', word)  # Remove punctuation
        if word_cleaned.lower() in PROFANE_WORDS:
            words[i] = mask_word(word_cleaned, severity)
    return " ".join(words)

def analyze_sentiment(text):
    """Predict sentiment using the trained sentiment model."""
    if not text.strip():
        return {"score": 0, "magnitude": 0}

    inputs = sentiment_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = sentiment_model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    sentiment_score = scores[0][1].item() - scores[0][0].item()  # Assuming binary classification (Negative vs Positive)
    magnitude = abs(sentiment_score)

    return {"score": sentiment_score, "magnitude": magnitude}

def classify_profanity(text):
    """Classify profanity severity using the profanity detection model."""
    inputs = profanity_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = profanity_model(**inputs)
        predicted_label = torch.argmax(outputs.logits, dim=1).item()

    return severity_mapping.get(predicted_label, "Non-Profane")

def analyze_severity(comments):
    """Analyze severity and sentiment for each comment, only displaying the masked text."""
    analyzed_comments = []
    profane_words = []
    negative_words = []
    non_profane_words = []
    
    for comment in comments:
        if not isinstance(comment, dict):  # Check if the comment is a dictionary
            continue  # Skip this comment if it isn't a dictionary

        text = comment.get('text', '')  # Get the text of the comment
        if not text:
            continue  # Skip if there's no text

        # Profanity classification
        severity = classify_profanity(text)
        
        # Sentiment Analysis
        sentiment = get_sentiment_with_pos(text)

        # Ensure sentiment dictionary has required keys
        sentiment_score = sentiment.get("Sentiment Score", 0)
        magnitude = sentiment.get("Magnitude", 0)

        # Mask the text for profanity
        masked_text = mask_profanity(text, severity)

        # Store results
        analyzed_comments.append({
            'masked_text': masked_text,  # Only include the masked text
            'severity': severity,
            "sentiment_score": sentiment_score,
            "magnitude": magnitude
        })
        
        # Categorize comments
        if severity.lower() != "non-profane":
            profane_words.append(text)
        else:
            non_profane_words.append(text)
            
        if sentiment_score < 0:
            negative_words.append(text)

    print("🔍 Analyzed Comments:", analyzed_comments)  # Debugging check

    return analyzed_comments, profane_words, negative_words, non_profane_words


import praw
import torch
import re
import random
from transformers import BertTokenizer, BertForSequenceClassification
from flask import Flask, request, redirect

REDDIT_CLIENT_ID = "kOUF4tzADqVoCJPuFRZPOA"
REDDIT_CLIENT_SECRET = "DDdP5fFRGi-7P7ZsEDDaQZhHVlNWbA"
REDDIT_USERNAME = "Budget_Doubt8362"
REDDIT_PASSWORD = "devinbooker123"
USER_AGENT = "profanity_filter_bot (by u/Budget_Doubt8362)"

MODEL_PATH = r"C:\Users\Personal Computer\Desktop\test-reddit-filtering\Bert_model"  # Change to your model path
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)

# Initialize Reddit bot
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent=USER_AGENT
)

LABEL_MAP = {0: "High", 1: "Mild", 2: "Moderate", 3: "Nonprofane"}

PROFANE_WORDS = [
    "puta", "putangina", "kupal", "tangina", "pakyu", "tarantado",
    "gago", "ulol", "tanga", "bobo", "punyeta", "pakshet",
    "bwiset","bwisit", "pucha", "yawa","tang ina"
]

# Flask app for Reddit API authorization
app = Flask(__name__)

@app.route('/reddit_callback')
def reddit_callback():
    code = request.args.get('code')
    if code:
        return f"Authorization successful! Your code: {code}"
    return "Authorization failed."

# Function to classify text using BERT
def classify_profanity(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    label = torch.argmax(outputs.logits).item()
    return LABEL_MAP[label]

# Function to mask profanity based on severity
def mask_word(word, severity):
    if severity == "High":
        return word[0] + "*" * (len(word) - 1)  
    elif severity == "Mild":
        if len(word) > 1:
            idx = random.randint(1, len(word) - 1)  
            return word[:idx] + "*" + word[idx + 1:]
        return word 
    elif severity == "Moderate":
        if len(word) > 2:
            indices = random.sample(range(1, len(word)), k=min(2, len(word) - 1))  
            masked_word = list(word)
            for idx in indices:
                masked_word[idx] = "*"
            return "".join(masked_word)
        return word  
    return word  

# Preprocessing function to clean text
def preprocess_text(text):
    text = text.lower()
    text = " ".join(text.split())
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'http\S+|www\S+|@\S+', '', text)
    return text

# Function to censor profanity
def censor_profanity(text, severity):
    def replace_match(match):
        word = match.group(0)
        return mask_word(word, severity)
    pattern = r'\b(' + '|'.join(re.escape(p) for p in PROFANE_WORDS) + r')\b'
    censored_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    return censored_text

# Monitor comments in the subreddit
def monitor_subreddit(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    print(f"🔍 Monitoring subreddit: {subreddit_name} for profane comments...")

    for comment in subreddit.stream.comments(skip_existing=True):
        comment_text = comment.body
        preprocessed_text = preprocess_text(comment_text)
        severity = classify_profanity(preprocessed_text)
        
        if severity != "Nonprofane":
            censored_text = censor_profanity(comment_text, severity)
            try:
                comment.mod.remove()
                print(f"❌ Removed comment {comment.id} due to {severity} profanity.")
                response = f"⚠️ This comment contained {severity} profanity and has been filtered.\n\nFiltered version: {censored_text}"
                comment.reply(response)
                print(f"✅ Replied to comment {comment.id}: {censored_text} (Severity: {severity})")
            except Exception as e:
                print(f"⚠️ Error processing comment {comment.id}: {e}")
        else:
            print(f"✔️ Comment {comment.id} is clean. Skipping...")

if __name__ == "__main__":
    monitor_subreddit("StudentDiscussion01")


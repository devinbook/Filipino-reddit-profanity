import praw
import torch
import re
import random
from transformers import BertTokenizer, BertForSequenceClassification

# Reddit API Credentials
REDDIT_CLIENT_ID = "kOUF4tzADqVoCJPuFRZPOA"
REDDIT_CLIENT_SECRET = "DDdP5fFRGi-7P7ZsEDDaQZhHVlNWbA"
REDDIT_USERNAME = "Budget_Doubt8362"
REDDIT_PASSWORD = "devinbooker123"
USER_AGENT = "profanity_filter_bot (by u/Budget_Doubt8362)"

# Load BERT model and tokenizer
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

# Map label indices to categories
LABEL_MAP = {0: "High", 1: "Mild", 2: "Moderate", 3: "Nonprofane"}

# List of profane words (Update with your actual dataset)
PROFANE_WORDS = ["gago", "putangina", "tangina", "bobo", "tanga", "ulol", "kupal", "bwisit","Tangina"]

# Function to classify text using BERT
def classify_profanity(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    label = torch.argmax(outputs.logits).item()
    return LABEL_MAP[label]

# Function to mask profanity based on severity
def mask_word(word, severity):
    """Mask a word based on profanity severity."""
    if severity == "High":
        return word[0] + "*" * (len(word) - 1)  # Keep first letter, mask the rest
    
    elif severity == "Mild":
        if len(word) > 1:
            idx = random.randint(1, len(word) - 1)  # Pick a random position to mask
            return word[:idx] + "*" + word[idx + 1:]
        return word  # Return unchanged if too short
    
    elif severity == "Moderate":
        if len(word) > 2:
            indices = random.sample(range(1, len(word)), k=min(2, len(word) - 1))  # Pick up to 2 letters
            masked_word = list(word)
            for idx in indices:
                masked_word[idx] = "*"
            return "".join(masked_word)
        return word  # Return unchanged if too short
    
    return word  # Return unchanged if severity is Nonprofane

# Preprocessing function to clean text
def preprocess_text(text):
    """Preprocess the input text before detecting profanity."""
    # Step 1: Lowercase all text
    text = text.lower()

    # Step 2: Remove extra spaces
    text = " ".join(text.split())

    # Step 3: Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Step 4: Remove URLs and mentions
    text = re.sub(r'http\S+|www\S+|@\S+', '', text)

    # Return preprocessed text
    return text

# Function to censor profanity
def censor_profanity(text, severity):
    def replace_match(match):
        word = match.group(0)
        return mask_word(word, severity)
    
    # Create a regex pattern for profanity detection
    pattern = r'\b(' + '|'.join(re.escape(p) for p in PROFANE_WORDS) + r')\b'
    
    # Replace profane words in the text
    censored_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    
    return censored_text

# Monitor comments in the subreddit
def monitor_subreddit(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    print(f"🔍 Monitoring subreddit: {subreddit_name} for profane comments...")

    for comment in subreddit.stream.comments(skip_existing=True):
        comment_text = comment.body
        preprocessed_text = preprocess_text(comment_text)  # Preprocess the comment text first
        severity = classify_profanity(preprocessed_text)  # Classify profanity severity
        
        if severity != "Nonprofane":  # Profanity detected
            censored_text = censor_profanity(comment_text, severity)

            try:
                # Remove the original comment (only works if bot is a mod)
                comment.mod.remove()
                print(f"❌ Removed comment {comment.id} due to {severity} profanity.")

                # Reply with the filtered version
                response = f"⚠️ This comment contained {severity} profanity and has been filtered.\n\nFiltered version: {censored_text}"
                comment.reply(response)
                print(f"✅ Replied to comment {comment.id}: {censored_text} (Severity: {severity})")

            except Exception as e:
                print(f"⚠️ Error processing comment {comment.id}: {e}")
        else:
            print(f"✔️ Comment {comment.id} is clean. Skipping...")

# Run the bot
if __name__ == "__main__":
    monitor_subreddit("StudentDiscussion01")   # Change this to your subreddit name

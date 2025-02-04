import re
import praw

# List of prohibited phrases to filter out
PROHIBITED_PHRASES = [
    "Giving out other people's personal and identifying information is STRICTLY PROHIBITED",
    "violates reddit rules",
    # Add any other prohibited phrases here
]

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"@\w+", "", text)  # Remove mentions
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # Normalize white spaces
    return text

def contains_prohibited_phrase(text):
    for phrase in PROHIBITED_PHRASES:
        if phrase.lower() in text.lower():
            return True
    return False

def fetch_reddit_comments(post_url):
    try:
        reddit = praw.Reddit(client_id="fl_6wvPC8PcnJ4buzYHePA",
                             client_secret="p_Z28aBGbePUpH7tJSTvVl9V0cbqRw",
                             user_agent="Profanity_tagalog_dataset")

        submission = reddit.submission(url=post_url)
        submission.comments.replace_more(limit=0)

        post_data = {
            "title": preprocess_text(submission.title),
            "content": preprocess_text(submission.selftext),
            "url": submission.url,
            "comments": []
        }

        # Loop through comments, anonymize author and filter prohibited content
        for comment in submission.comments.list():
            if comment.author and comment.author.name != "AutoModerator":
                cleaned_text = preprocess_text(comment.body)

                # Skip comments with prohibited phrases
                if contains_prohibited_phrase(cleaned_text):
                    continue

                post_data["comments"].append({
                    # Do not include user data or anonymize it
                    "user": "Anonymous",  # Replace with "Anonymous" or remove
                    "text": cleaned_text
                })

        return post_data
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return None

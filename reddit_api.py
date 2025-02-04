import re
import praw

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"@\w+", "", text)  
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  
    text = re.sub(r"\s+", " ", text).strip()  
    return text

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

        for comment in submission.comments.list():
            if comment.author and comment.author.name != "AutoModerator":
                cleaned_text = preprocess_text(comment.body)
                post_data["comments"].append({
                    "user": comment.author.name,
                    "text": cleaned_text
                })

        return post_data
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return None

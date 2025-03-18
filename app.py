from flask import Flask, render_template, request
from reddit_api import fetch_reddit_comments
from profanity_model import analyze_severity
import os
from wordcloud import WordCloud, STOPWORDS

app = Flask(__name__)

# Function to map severity to row color
def get_row_color(severity):
    return {
        "High": "bg-red-200",
        "Moderate": "bg-yellow-200",
        "Mild": "bg-cyan-200",
        "Non-Profane": "bg-green-200"
    }.get(severity, "bg-white")

# Function to map severity to insights
def get_insight(severity):
    return {
        "High": "Immediate reporting is recommended due to the highly offensive nature of the content.",
        "Moderate": "Monitor the comment and consider issuing a warning.",
        "Mild": "The content is slightly offensive.",
        "Non-Profane": "The comment does not contain profanity."
    }.get(severity, "No recommendation available.")

# Function to generate a word cloud and save it as an image
def generate_wordcloud(words, filename):
    if not words:
        return None

    stopwords = set(STOPWORDS)  # English stopwords
    tagalog_stopwords = {"sa", "na", "ng", "yung", "mga", "at", "ay", "siya", "ko", "mo",
    "tayo", "sila", "kayo", "natin", "akin", "kanila", "ating", "ganyan",
    "ito", "iyan", "doon", "dito", "diyan", "kasi", "lang", "din", "rin",
    "nga", "pero", "wala", "may", "dapat", "para", "niya", "ni", "bakit","ang","sya","ka","ako","pa"}  # Tagalog stopwords
    stopwords.update(tagalog_stopwords)

    text = " ".join(words)
    wordcloud = WordCloud(width=350, height=350, background_color="white", max_words=30, stopwords=stopwords).generate(text)

    img_path = f"static/{filename}"
    wordcloud.to_file(img_path)  # Save word cloud image

    return f"/{img_path}"  # Return the image path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    subreddit_url = request.form['reddit_url']
    post_data = fetch_reddit_comments(subreddit_url)

    if not post_data:
        return "Error fetching Reddit post."

    analyzed_comments, profane_words, negative_words, non_profane_words = analyze_severity(post_data["comments"])

    # Count total comments and comments with profanity
    total_comments = len(analyzed_comments)
    profane_comment_count = sum(1 for comment in analyzed_comments if comment["severity"] in ["High", "Moderate", "Mild"])

    # Ensure row color and insight are applied
    for comment in analyzed_comments:
        comment["row_color"] = get_row_color(comment["severity"])
        comment["insight"] = get_insight(comment["severity"])

    # Generate Word Clouds
    all_profane_words = profane_words + negative_words
    profane_wordcloud_img = generate_wordcloud(all_profane_words, "profane_wordcloud.png")
    non_profane_wordcloud_img = generate_wordcloud(non_profane_words, "non_profane_wordcloud.png")

    return render_template(
        'results.html',
        post=post_data,
        comments=analyzed_comments,
        profane_wordcloud_img=profane_wordcloud_img,
        non_profane_wordcloud_img=non_profane_wordcloud_img,
        total_comments=total_comments,
        profane_comment_count=profane_comment_count
    )


if __name__ == '__main__':
    app.run(debug=True)

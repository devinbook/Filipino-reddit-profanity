from flask import Flask, render_template, request, jsonify
from reddit_api import fetch_reddit_comments
from profanity_model import analyze_severity
import io

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    subreddit_url = request.form['reddit_url']
    post_data = fetch_reddit_comments(subreddit_url)

    if not post_data:
        return "Error fetching Reddit post."

    analyzed_comments = analyze_severity(post_data["comments"])

    for comment in analyzed_comments:
        severity = comment['severity']
        comment['row_color'] = get_row_color(severity)
        comment['insight'] = get_insight(severity)

    return render_template('results.html', post=post_data, comments=analyzed_comments)

if __name__ == '__main__':
    app.run(debug=True)

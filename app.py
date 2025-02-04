from flask import Flask, render_template, request
from reddit_api import fetch_reddit_comments
from profanity_model import analyze_severity

app = Flask(__name__)

# Function to map severity to row color
def get_row_color(severity):
    if severity == "High":
        return "bg-red-200"  # High severity -> red
    elif severity == "Moderate":
        return "bg-yellow-200"  # Moderate severity -> yellow
    elif severity == "Mild":
        return "bg-cyan-200"  # Mild severity -> cyan
    elif severity == "Non-Profane":
        return "bg-green-200"  # Non-profane -> green
    else:
        return "bg-white"  # Default color (if something goes wrong)

# Function to map severity to insights
def get_insight(severity):
    if severity == "High":
        return "Immediate reporting or flagging is recommended due to the highly offensive nature of the content." 
    elif severity == "Moderate":
        return "Monitor the comment and consider issuing a warning or reminder about community guidelines."
    elif severity == "Mild":
        return "The content is slightly offensive."
    elif severity == "Non-Profane":
        return "The comment does not contain profanity."
    else:
        return "No recommendation available."
    
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

    # Add the row color and insight for each analyzed comment
    for comment in analyzed_comments:
        severity = comment['severity']
        comment['row_color'] = get_row_color(severity)
        comment['insight'] = get_insight(severity)

    # Pass the post details + analyzed comments to the template
    return render_template('results.html', post=post_data, comments=analyzed_comments)


if __name__ == '__main__':
    app.run(debug=True)



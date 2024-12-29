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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    subreddit_url = request.form['reddit_url']
    comments = fetch_reddit_comments(subreddit_url)
    analyzed_comments = analyze_severity(comments)

    # Add the row color to each analyzed comment
    for comment in analyzed_comments:
        severity = comment['severity']
        row_color = get_row_color(severity)
        comment['row_color'] = row_color

    return render_template('results.html', comments=analyzed_comments)

if __name__ == '__main__':
    app.run(debug=True)

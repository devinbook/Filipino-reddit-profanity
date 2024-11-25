from flask import Flask, request, jsonify, render_template
from profanity_model import detect_profanity
from reddit_api import fetch_reddit_comments

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check_reddit_profanity", methods=["POST"])
def check_reddit_profanity():
    data = request.json
    post_url = data.get("post_url")

    # Fetch comments from Reddit
    comments = fetch_reddit_comments(post_url)
    results = []

    # Check each comment for profanity
    for comment in comments:
        is_profane = detect_profanity(comment)
        results.append({
            "comment": comment,
            "profane": "Yes" if is_profane else "No"
        })

    # Render the results on a separate HTML page
    return render_template("results.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)

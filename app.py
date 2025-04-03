from flask import Flask, render_template, request
from reddit_api import fetch_reddit_comments
from profanity_model import analyze_severity
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import numpy as np
import os

app = Flask(__name__)

# Ensure 'static/' folder exists for word cloud images
if not os.path.exists('static'):
    os.makedirs('static')

# Load and process mask for word cloud
def load_and_process_mask(mask_path):
    mask_image = Image.open(mask_path).convert("L")
    
    # Resize the mask to match the profanity graph size (1200x600)
    mask_image = mask_image.resize((1200, 600))
    mask_array = np.array(mask_image)

    # Ensure mask is white background (255) and black shape (0)
    mask_array = np.where(mask_array > 128, 255, 0)

    return mask_array

def get_row_color(severity):
    return {
        "High": "bg-red-200",
        "Moderate": "bg-yellow-200",
        "Mild": "bg-cyan-200",
        "Non-Profane": "bg-green-200"
    }.get(severity, "bg-white")

# Function to generate slanted word cloud with adjusted size
def generate_slanted_word_cloud(words, filename):
    if not words:
        return None

    mask_path = "static/twitter-bird.png"  # Path to your mask
    font_path = "static/LEMONMILK-Bold.otf"  # Path to your custom font

    mask = load_and_process_mask(mask_path)

    stopwords = set(STOPWORDS)
    tagalog_stopwords = {
        "sa", "na", "ng", "yung", "mga", "at", "ay", "siya", "ko", "mo",
        "tayo", "sila", "kayo", "natin", "akin", "kanila", "ating", "ito",
        "iyan", "doon", "dito", "diyan", "kasi", "lang", "din", "rin", "nga",
        "pero", "wala", "may", "dapat", "para", "niya", "ni", "bakit",
        "ang", "sya", "ka", "ako", "pa"
    }
    stopwords.update(tagalog_stopwords)

    text = " ".join(words)

    wordcloud = WordCloud(
        width=1200,  # Match graph width
        height=600,  # Match graph height
        mask=mask,
        background_color="white",
        contour_width=2,
        contour_color="white",
        max_words=200,
        colormap="inferno",  # Customize the color map
        stopwords=stopwords,
        min_font_size=10,
        max_font_size=150,
        prefer_horizontal=0.6,  # Adjust slant angle (0=vertical, 1=horizontal)
        random_state=42,
        font_path=font_path
    ).generate(text)

    img_path = f"static/{filename}"
    wordcloud.to_file(img_path)  # Save the word cloud image

    return f"/{img_path}"  # Return the image path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    subreddit_url = request.form['reddit_url']
    
    # Fetch Reddit comments using PRAW (from reddit_api.py)
    post_data = fetch_reddit_comments(subreddit_url)

    if not post_data:
        return "Error fetching Reddit post."

    # Analyze comment severity (from profanity_model.py)
    analyzed_comments, profane_words, negative_words, non_profane_words = analyze_severity(post_data["comments"])
    for comment in analyzed_comments:
        comment["row_color"] = get_row_color(comment["severity"])
        
    # Count total comments and comments with profanity
    total_comments = len(analyzed_comments)
    profane_comment_count = sum(1 for comment in analyzed_comments if comment["severity"] in ["High", "Moderate", "Mild"])
    
    # Debugging output
    print(f"Total Comments: {total_comments}")
    print(f"Profane Comments: {profane_comment_count}")
    
    # Combine profane and negative words
    all_profane_and_negative_words = profane_words + negative_words

    # Generate a custom slanted word cloud with adjusted size
    profane_wordcloud_img = generate_slanted_word_cloud(all_profane_and_negative_words, "profane_wordcloud.png")

    return render_template(
        'results.html',
        post=post_data,
        comments=analyzed_comments,
        profane_wordcloud_img=profane_wordcloud_img,
        total_comments=total_comments,
        profane_comment_count=profane_comment_count
    )


if __name__ == '__main__':
    app.run(debug=True)

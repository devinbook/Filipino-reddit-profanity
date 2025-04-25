import re

def detect_aspect(comment_text):
    if not comment_text or not isinstance(comment_text, str):
        return "Unknown"

    lowered = comment_text.lower()

    aspect_keywords = {
        "Politics": [
            "gobyerno", "presidente", "senador", "politiko", "mayor",
            "duterte", "bbm", "leni", "robredo", "marcos", "vico", "sotto"
        ],
        "Gender": [
            "babae", "lalaki", "bakla", "bayot", "tomboy", "girl", "boy"
        ],
        "Religion": [
            r"\bdiyos\b", r"\bsimbahan\b", r"\bpari\b", r"\bmuslim\b", 
            r"\bkristiyano\b", r"\binc\b", r"\bcatholic\b", r"\biglesia\b"
        ],
        "User": [
            r"\bikaw\b", r"\bmo\b", r"\bka\b", "tanga ka", "gago ka", "ulol ka", "drivers"
        ],
        "Class": [
            "mahirap", "mayaman", "elitista", "masa", "burgis", "social climber"
        ],
        "Entertainment/Org": [
            r"\bkapamilya\b", r"\bgma\b", r"\babs\b", r"\btv5\b"
        ],
        "Others": []  # fallback category
    }

    for aspect, keywords in aspect_keywords.items():
        for keyword in keywords:
            # Match using regular expressions with word boundaries
            if re.search(keyword if keyword.startswith(r"\b") else fr"\b{keyword}\b", lowered):
                return aspect

    return "Other"

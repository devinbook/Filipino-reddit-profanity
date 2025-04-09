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
        "diyos", "simbahan", "pari", "muslim", "kristiyano", "inc", "catholic", "iglesia"
    ],
    "User": [
        "ikaw", "mo", "ka", "tanga ka", "gago ka", "ulol ka", "drivers"
    ],
    "Class": [
        "mahirap", "mayaman", "elitista", "masa", "burgis", "social climber"
    ],
    "Entertainment/Org": [
        "kapamilya", "gma", "abs", "tv5"
    ],
    "Others": []  # fallback category for uncategorized terms
}


    for aspect, keywords in aspect_keywords.items():
        if any(keyword in lowered for keyword in keywords):
            return aspect

    return "Other"

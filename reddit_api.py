import praw

def fetch_reddit_comments(post_url):
    try:
        reddit = praw.Reddit(client_id='fl_6wvPC8PcnJ4buzYHePA',
                     client_secret='p_Z28aBGbePUpH7tJSTvVl9V0cbqRw',
                     user_agent='Profanity_tagalog_dataset')
        submission = reddit.submission(url=post_url)
        submission.comments.replace_more(limit=0)

        comments = []
        for comment in submission.comments.list():
            if comment.author and comment.author.name != 'AutoModerator':
                comments.append({"user": comment.author.name, "text": comment.body})
        return comments
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

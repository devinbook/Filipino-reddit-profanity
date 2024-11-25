import praw

def fetch_reddit_comments(post_url):
    reddit = praw.Reddit(client_id='uLfq7N-Kp-n_noaXUDVuTg',
                         client_secret='IUhw5TKGpWeRI2yweNOEwuzeIVVi8A',
                         user_agent='Profanity_tagalog')

    submission = reddit.submission(url=post_url)
    submission.comments.replace_more(limit=0) 
    comments = [
        comment.body 
        for comment in submission.comments.list() 
        if comment.author and comment.author.name != 'AutoModerator' and not comment.stickied
    ]
    
    return comments
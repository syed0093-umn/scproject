import praw
import time
import json
import logging

import os
from phase_1_setup import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)


def fetch_subreddit_posts(subreddit_name, months=6, limit=10000):
    """
    Fetch posts from the specified subreddit within the past 'months' months.
    Iterates through the newest posts and stops once posts older than the threshold are encountered.
    """
    logging.info(f"Fetching posts from r/{subreddit_name}...")
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    current_time = time.time()
    six_months_ago = current_time - (months * 30 * 24 * 60 * 60)
    
    # Using subreddit.new() to get the most recent posts first.
    for submission in subreddit.new(limit=limit):
        if submission.created_utc < six_months_ago:
            break
        post_data = {
            "id": submission.id,
            "title": submission.title,
            "url": submission.url,
            "created_utc": submission.created_utc,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "subreddit": subreddit_name,
            "author": str(submission.author)
        }
        posts.append(post_data)
    
    logging.info(f"Fetched {len(posts)} posts from r/{subreddit_name}.")
    return posts

news_posts = fetch_subreddit_posts('news', months=6, limit=10000)
clickbait_posts = fetch_subreddit_posts('SavedYouAClick', months=6, limit=10000)

with open('news_posts.json', 'w') as f:
    json.dump(news_posts, f, indent=4)
with open('clickbait_posts.json', 'w') as f:
    json.dump(clickbait_posts, f, indent=4)

logging.info("Data extraction complete. JSON files saved.")
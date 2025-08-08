import os
import praw
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import time
from dotenv import load_dotenv

load_dotenv()

post_limit = int(input("Number of posts to scrape: "))

# === Configuration ===
SUBREDDIT_NAME = "Fitness_India"  # Change as needed
POST_LIMIT = post_limit  # Number of posts to fetch
OUTPUT_DIR = "data"

LAST_POST_FILE = os.path.join(OUTPUT_DIR, f"{SUBREDDIT_NAME}_last_post_fullname.txt")

def load_last_post_fullname():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            fullname = f.read().strip()
            if fullname:
                return fullname
    return None

def save_last_post_fullname(fullname):
    with open(LAST_POST_FILE, "w") as f:
        f.write(fullname)

# === Reddit API credentials ===
reddit = praw.Reddit(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET"),
    user_agent = "MyScraper by /u/dernox47"
)

# Rate limiting parameters
MAX_CALLS = 60
PERIOD = 60  # seconds
call_times = []

def rate_limited_call(func, *args, **kwargs):
    global call_times
    now = time.time()
    # Remove timestamps older than PERIOD
    call_times = [t for t in call_times if now - t < PERIOD]
    if len(call_times) >= MAX_CALLS:
        sleep_time = PERIOD - (now - call_times[0])
        if sleep_time > 0:
            time.sleep(sleep_time)
        now = time.time()
        call_times = [t for t in call_times if now - t < PERIOD]
    call_times.append(time.time())
    return func(*args, **kwargs)

def fetch_post_data(post):
    return {
        "post_id": post.id,
        "title": post.title,
        "author": str(post.author),
        "score": post.score,
        "upvote_ratio": post.upvote_ratio,
        "num_comments": post.num_comments,
        "created_utc": datetime.fromtimestamp(post.created_utc),
        "selftext": post.selftext,
        "url": post.url,
        "permalink": post.permalink,
        "is_self": post.is_self,
        "flair": post.link_flair_text
    }

def fetch_comment_data(post_id, comment):
    return {
        "post_id": post_id,
        "comment_id": comment.id,
        "author": str(comment.author),
        "body": comment.body,
        "score": comment.score,
        "created_utc": datetime.fromtimestamp(comment.created_utc),
        "parent_id": comment.parent_id,
    }

# === Ensure output folder exists ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Scrape posts and comments ===
posts_data = []
comments_data = []

subreddit = reddit.subreddit(SUBREDDIT_NAME)

last_fullname = load_last_post_fullname()

def fetch_posts(after_fullname):
    if after_fullname:
        return list(subreddit.new(limit=POST_LIMIT, params={"after": after_fullname}))
    else:
        return list(subreddit.new(limit=POST_LIMIT))

# Use rate_limited_call to fetch posts listing with incremental scraping
posts = rate_limited_call(fetch_posts, last_fullname)

for post in tqdm(posts, desc="Posts", unit="post"):
    posts_data.append(fetch_post_data(post))

    # Use rate_limited_call for replace_more (counts as API call)
    rate_limited_call(post.comments.replace_more, limit=None)

    for comment in tqdm(post.comments.list(), desc=f"Comments for {post.id}", leave=False):
        comments_data.append(fetch_comment_data(post.id, comment))

if posts:
    save_last_post_fullname(posts[-1].fullname)

# === Convert to DataFrames ===
df_posts = pd.DataFrame(posts_data)
df_comments = pd.DataFrame(comments_data)

# === Save to Excel with two sheets, append if file exists ===
filename = os.path.join(OUTPUT_DIR, f"{SUBREDDIT_NAME}_posts_and_comments.xlsx")

if os.path.exists(filename):
    try:
        existing_posts = pd.read_excel(filename, sheet_name="Posts")
    except Exception:
        existing_posts = pd.DataFrame()
    try:
        existing_comments = pd.read_excel(filename, sheet_name="Comments")
    except Exception:
        existing_comments = pd.DataFrame()
    df_posts = pd.concat([existing_posts, df_posts], ignore_index=True)
    df_comments = pd.concat([existing_comments, df_comments], ignore_index=True)

with pd.ExcelWriter(filename) as writer:
    df_posts.to_excel(writer, sheet_name="Posts", index=False)
    df_comments.to_excel(writer, sheet_name="Comments", index=False)

print(f"✅ Saved {len(df_posts)} posts and {len(df_comments)} comments to {filename}")
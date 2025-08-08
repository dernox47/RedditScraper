import os
import praw
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# === Configuration ===
SUBREDDIT_NAME = "Fitness_India"  # Change as needed
POST_LIMIT = 10  # Number of posts to fetch
OUTPUT_DIR = "data"

# === Reddit API credentials ===
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="MyScraper by /u/dernox47"
)

# === Ensure output folder exists ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Scrape posts and comments ===
posts_data = []
comments_data = []

subreddit = reddit.subreddit(SUBREDDIT_NAME)

# You can use: .hot(), .new(), .top(), .rising()
for post in tqdm(subreddit.new(limit=POST_LIMIT), desc="Posts", unit="post"):
        posts_data.append({
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
        })

        # Load all comments (replace "MoreComments" with actual comments)
        post.comments.replace_more(limit=None)

        for comment in tqdm(post.comments.list(), desc=f"Comments for {post.id}", leave=False):
            comments_data.append({
                "post_id": post.id,
                "comment_id": comment.id,
                "author": str(comment.author),
                "body": comment.body,
                "score": comment.score,
                "created_utc": datetime.fromtimestamp(comment.created_utc),
                "parent_id": comment.parent_id,
            })


# === Convert to DataFrames ===
df_posts = pd.DataFrame(posts_data)
df_comments = pd.DataFrame(comments_data)

# === Save to Excel with two sheets ===
filename = os.path.join(OUTPUT_DIR, f"{SUBREDDIT_NAME}_posts_and_comments.xlsx")
with pd.ExcelWriter(filename) as writer:
    df_posts.to_excel(writer, sheet_name="Posts", index=False)
    df_comments.to_excel(writer, sheet_name="Comments", index=False)

print(f"✅ Saved {len(df_posts)} posts and {len(df_comments)} comments to {filename}")
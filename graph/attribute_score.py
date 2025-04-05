from graph.pg_reddit_driver import RedditDB
from graph.reddit import RedditWrapper
from llms import compute_post_score, is_post_intresting
import praw


def process_most_commented():
    db = RedditDB()
    reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")
    wrapper = RedditWrapper(db, reddit)

    sub = reddit.subreddit("news")

    for p in sub.controversial(time_filter="year"):
        wrapper.treat_submission(p, 2)


if __name__ == "__main__":
    process_most_commented(db)

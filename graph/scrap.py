from graph.reddit import RedditWrapper
import praw
from graph.pg_reddit_driver import RedditDB
from graph.threading_scrapper import ThreadedScraper


def scrap():
    db = RedditDB()
    reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")
    wrapper = RedditWrapper(db, reddit)

    posts = db.get_posts()

    # sub = reddit.subreddit("news")

    def save_post(p):
        wrapper.treat_submission(p, 100, 100)

    scrapper = ThreadedScraper(save_post, None)

    # for p in sub.controversial(time_filter="week", limit=100):
    #     scrapper.process_post(p)

    for post in posts:
        p = reddit.models.Submission(post.id)

    scrapper.wait_all()

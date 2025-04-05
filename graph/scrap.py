from graph.reddit import RedditWrapper
import praw
from graph.pg_reddit_driver import RedditDB
from graph.threading import ThreadedScraper


def scrap():
    db = RedditDB()
    reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")
    wrapper = RedditWrapper(db, reddit)

    sub = reddit.subreddit("news")

    def save_post(p):
        wrapper.treat_submission(p, 4, 1)

    scrapper = ThreadedScraper(save_post, 5)

    for p in sub.top(time_filter="week", limit=1):
        scrapper.process_post(p)

    scrapper.wait_all()

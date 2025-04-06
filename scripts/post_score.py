from graph.pg_reddit_driver import RedditDB
from graph.reddit import RedditWrapper
from graph.threading_scrapper import ThreadedScraper
from llms import compute_post_score, is_post_interesting
import praw


def post_score():
    db = RedditDB()
    reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")
    wrapper = RedditWrapper(db, reddit)

    sub = reddit.subreddit("news")

    def process_post(p):
        post = db.get_post(p["id"])

        if post:
            db.mark_post_as_treated(post[0])

            if is_post_interesting(post):
                score = compute_post_score(post)
                db.update_post_score(post[0], score)

    scrapper = ThreadedScraper(process_post, max_workers=32)

    # for p in sub.controversial(time_filter="month", limit=100):
    #     scrapper.process_post(p)

    for p in db.get_most_commented_unprocessed_post(limit=2000):
        # print(p)
        scrapper.process_post({"id": p[0]})

    scrapper.wait_all()

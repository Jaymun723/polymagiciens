from graph.pg_reddit_driver import RedditDB
from graph.reddit import RedditWrapper
from graph.threading_scrapper import ThreadedScraper
from llms import compute_post_score, is_post_interesting
import praw


def attribute_score():
    db = RedditDB()
    reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")
    wrapper = RedditWrapper(db, reddit)

    sub = reddit.subreddit("news")

    def process_post(p):
        print("Finished tree")
        post = db.get_post(p.id)

        db.mark_post_as_treated(post[0])

        if is_post_interesting(post):
            wrapper.treat_submission(p, 40, 10)
            print("It's intresting !")
            print(post[2])
            score = compute_post_score(post)
            print(score)
            db.update_post_score(post[0], score)
        else:
            print("It's not intresting.")

    scrapper = ThreadedScraper(process_post, max_workers=32)

    for p in sub.controversial(time_filter="month", limit=100):
        scrapper.process_post(p)

    scrapper.wait_all()

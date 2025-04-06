from graph.reddit import RedditWrapper
from graph.pg_reddit_driver import RedditDB
import praw


def investigate_user():
    reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")
    db = RedditDB()
    wrapper = RedditWrapper(db, reddit)

    user_id = input("Entre the user id:")

    u = reddit.redditor(user_id)

    wrapper.treat_user(u, 10, 10)

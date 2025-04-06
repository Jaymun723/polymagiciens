from graph.pg_reddit_driver import RedditDB
from llms.match_score.comment_nli import comment_score as multiplier_score
from graph.reddit import RedditWrapper
import praw


def comment_score():
    db = RedditDB()
    reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")

    posts = db.get_treated_posts_ordered_by_comments()
    print(f"There are {len(posts)} to deal with.")

    for p in posts:
        wrapper = RedditWrapper(db, reddit)
        wrapper.treat_submission(reddit.submission(p[0]), 1, save_post=False)

        comments = db.get_comments_by_post_id(p[0])
        print(f"Post {p[0]} has {len(comments)} attached.")
        for comment in comments:
            post_str = f"Title: {p[2]}\n{p[3]}"
            comment_str = comment[3]
            multiplier = multiplier_score(post_str, comment_str)
            scaled_score = multiplier * (p[6] / 100)  # score
            score = int(scaled_score * 50 + 50)
            db.update_comment_score(comment[0], score)

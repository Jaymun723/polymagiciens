from graph.pg_reddit_driver import RedditDB
from llms.match_score.comment_nli import comment_score as multiplier_score


def comment_score():
    db = RedditDB()

    posts = db.get_treated_posts_ordered_by_comments()
    print(f"There are {len(posts)} to deal with.")

    for p in posts:
        comments = db.get_comments_by_post_id(p[0])
        for comment in comments:
            post_str = f"Title: {p[2]}\n{p[3]}"
            comment_str = comment[3]
            multiplier = multiplier_score(post_str, comment_str)
            scaled_score = multiplier * (p[6] / 100)  # score
            score = int(scaled_score * 50 + 50)
            db.update_comment_score(comment[0], score)

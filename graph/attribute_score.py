from graph import RedditDB
from graph.reddit import scrap_post
from llms import compute_post_score, is_post_intresting


def process_most_commented(db):
    post = db.get_most_commented_unprocessed_post()
    db.mark_post_as_treated(post.id)
    if is_post_intresting(post.title, post.content, post.date):
        score = compute_post_score(post)
        db.update_post_score(post.id, score)
        scrap_post(post.id)


if __name__ == "__main__":
    db = RedditDB()
    process_most_commented(db)

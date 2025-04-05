from llms.Fact_check_v2 import post_to_grade


def is_post_intresting(post):
    post_title = post["title"]
    post_content = post["content"]
    post_date = post["date"]
    return True


def compute_post_score(post):
    post_title = post["title"]
    post_content = post["content"]
    post_date = post["date"]

    return post_to_grade(post_title, post_content, post_date)

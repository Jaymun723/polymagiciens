from llms.Fact_check_v2 import post_to_grade
from llms.llm_relevancy_deg import requete_is_relevant


def is_post_intresting(post):
    post_title = post[2]
    post_content = post[3]
    post_subreddit = post[4]

    query = f"The post was posted on {post_subreddit}\nTitle: {post_title}\nContent: {post_content}"

    return requete_is_relevant(query)


def compute_post_score(post):
    post_title = post[2]
    post_content = post[3]
    post_date = str(post[8])

    return post_to_grade(post_title, post_content, post_date)

from llms.request_factcheck import reddit_factchecking
import llms.agents_config.agent_is_relevant as agent1
from llms.request_to_agent import request_to_agent


def is_post_intresting(post):
    post_title = post[2]
    post_content = post[3]

    query = f"Title: {post_title}\n{post_content}"

    return request_to_agent(query, agent1)


def compute_post_score(post):
    post_title = post[2]
    post_content = post[3]
    post_date = str(post[8])

    return reddit_factchecking(post_title, post_content, post_date)

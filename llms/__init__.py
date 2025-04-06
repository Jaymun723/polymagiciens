from llms.Fact_check_v2 import post_to_grade
import llms.agents_config.agent_is_relevant as agent1
from llms.request_to_agent import request_to_agent 

def is_post_intresting(post):
    post_title = post["title"]
    post_content = post["content"]
    return request_to_agent(post_title + " " + post_content, agent1)

def compute_post_score(post):
    post_title = post["title"]
    post_content = post["content"]
    post_date = post["date"]

    return post_to_grade(post_title, post_content, post_date)

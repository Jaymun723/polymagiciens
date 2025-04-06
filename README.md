# Polymagiciens

## Code structure

In the `graph` folder there is the code in charge of scrapping reddit, adding the users, posts and comments to the database (`pg_reddit_driver.py` and `reddit.py`). There are also visualisation code: `create_graph.py` and `write_csv.py`.

In the `llms` folder there is the code in charge of evaluating if a post is misinformation or not (`request_factcheck.py` and `request_to_agent.py`) and the code giving a score for a comment based on the post (code inside `match_score`).

In the `scripts` folder there are the programs scrapping reddit and the ones computing the scores of the posts and the comments.

## The stack

- Main code run on a EC2 instance.
- Database on PostgreSQL : AWS RDS
- AI model on SageMaker endpoint
- AI agents using Mistral trainned with NeMo.
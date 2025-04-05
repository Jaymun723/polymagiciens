# Polymagiciens

## Code structure

In the `graph` folder there is the code in charge of scrapping reddit, adding the users, posts and comments to the database (`pg_reddit_driver.py` and `reddit.py`). There are also visualisation code: `create_graph.py` and `write_csv.py`.

In the `llms` folder there is the code in charge of evaluating if a post is misinformation or not (`Fact_check_v2.py` and `evaluate_misinformation.py`).

## Todo

- [] `is_interesting`
- [] `is_comment_relevant`
- [] `network_score`

## Notes

## The stack

Main code : EC2 instance
PostgreSQL : AWS RDS
AI custom model : SageMaker / Bedrock ?

Le problème de comment_nli.py c'est qu'il tourne en local, on veut le faire tourner sur AWS.
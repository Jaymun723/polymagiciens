# Polymagiciens

## Code structure

```
polymagiciens
├── graph
│   ├── build_graph.py # Read graph from the database and outputs in csv
│   ├── lissage.py # Apply "lissage" procedure to the nodes
│   ├── pg_reddit_driver.py # Driver between the database and reddit query
│   ├── reddit.py # The reddit scrapper
│   └── threading_scrapper.py # Helper class to speed up process with multithreading
├── llms
│   ├── agents_config
│   │   ├── agent_from_wikipedia.py
│   │   ├── agent_is_relevant.py
│   │   └── agent_to_wikipedia.py
│   ├── match_score
│   │   ├── comment_nli.py
│   │   ├── comment_nli_cloud.py
│   │   └── deployer_aws_sagemaker.py # Helper file to deploy code to aws sagemaker
│   ├── request_factcheck.py
│   └── request_to_agent.py
├── output
│   ├── edges.csv
│   └── nodes.csv
├── scripts
│   ├── build_graph.py
│   ├── comment_score.py
│   ├── display_graph.py
│   ├── post_score.py
│   └── scrap.py
├── README.md
├── Victor's Key.pem
├── aws.bash
├── edges.csv
├── main.py
├── nodes.csv
└── requirements.txt
```

In the `graph` folder there is the code in charge of scrapping reddit, adding the users, posts and comments to the database (`pg_reddit_driver.py` and `reddit.py`). There are also visualisation code: `create_graph.py` and `write_csv.py`.

In the `llms` folder there is the code in charge of evaluating if a post is misinformation or not (`request_factcheck.py` and `request_to_agent.py`) and the code giving a score for a comment based on the post (code inside `match_score`).

In the `scripts` folder there are the programs scrapping reddit and the ones computing the scores of the posts and the comments.

## The stack

- Main code run on a EC2 instance.
- Database on PostgreSQL : AWS RDS
- AI model on SageMaker endpoint
- AI agents using Mistral trainned with NeMo.
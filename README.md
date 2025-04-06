# FakeNet 

> AI-powered system that detects fake news, maps influence networks, and identifies bad actors.

## Code structure

```
FakeNet
├── graph
│   ├── build_graph.py # Read graph from the database and outputs in csv
│   ├── lissage.py # Apply "lissage" procedure to the nodes
│   ├── pg_reddit_driver.py # Driver between the database and reddit query
│   ├── reddit.py # The reddit scrapper
│   └── threading_scrapper.py # Helper class to speed up process with multithreading
├── llms
│   ├── agents_config
│   │   ├── agent_from_wikipedia.py # Local config of Mistral Agent using context from Wikipedia
│   │   ├── agent_is_relevant.py # Local config of Nemo Agent using Reddit post to propose relevancy score
│   │   └── agent_to_wikipedia.py # Local config of Mistral Agent using Reddit post to propose Wikipedia pages to browse
│   ├── match_score
│   │   ├── comment_nli.py # Run "roberta" model localy
│   │   ├── comment_nli_cloud.py # Run "roberta" model on AWS SageMaker
│   │   └── deployer_aws_sagemaker.py # Helper file to deploy code to AWS SageMaker
│   ├── request_factcheck.py # Multi-agentic online checker for fake news
│   └── request_to_agent.py # Mistral prompt from request and agent config
├── output # Contains csv, and graph visualisation
│   └── ...
├── scripts
│   ├── build_graph.py # Build graph nodes & edges csv
│   ├── comment_score.py # Compute the score of the comments
│   ├── display_graph.py # Create the visualisation of the graph
│   ├── post_score.py # Compute the score of the posts
│   └── scrap.py # Scrap reddit
├── README.md # This !
├── main.py # Entry file
└── requirements.txt
```

## The stack

- Main code run on a **EC2** instance.
- Database on **PostgreSQL** : **AWS RDS**
- AI model on **AWS SageMaker AI** endpoint
- AI agents using **Mistral** trainned with **NeMo**.

## Usage

You must first setup environement variables for AWS and Mistral and PostgreSQL connection.

```sh
python main.py script-name
```
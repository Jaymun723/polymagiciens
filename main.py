import argparse
from scripts.scrap import scrap
from scripts.post_score import post_score
from scripts.comment_score import comment_score
from scripts.build_graph import build_graph
from scripts.display_graph import display_graph

# Mapping from CLI argument to actual function
FUNCTION_MAP = {
    "scrap": scrap,
    "post-score": post_score,
    "comment-score": comment_score,
    "build-graph": build_graph,
}


def main():
    parser = argparse.ArgumentParser(
        description="Run a specific function from the scripts."
    )
    parser.add_argument(
        "script", help="The script name to run (scrap, post-score, comment-score)"
    )
    args = parser.parse_args()

    func = FUNCTION_MAP.get(args.script)
    if func is None:
        print(
            f"Error: Unknown script '{args.script}'. Available options: {', '.join(FUNCTION_MAP.keys())}"
        )
        exit(1)

    func()


if __name__ == "__main__":
    main()

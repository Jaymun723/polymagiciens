from graph import RedditDB
import pandas

db = RedditDB()

users = db.get_users()

vertices = pandas.DataFrame(
    {"id": [u[0] for u in users], "label": [u[1] for u in users]}
)

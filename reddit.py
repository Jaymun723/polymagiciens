import praw
import psycopg
from psycopg import sql


class RedditDB:
	def __init__(
		self,
		user="postgres",
		db_name="reddit_data",
		host="/var/run/postgresql",
		port="5432",
	):
		self.user = user
		self.db_name = db_name
		self.host = host
		self.port = port

		# Step 1: Connect to 'postgres' to check/create the target DB
		with psycopg.connect(
			dbname="postgres",
			user=self.user,
			host=self.host,
			port=self.port,
			autocommit=True,
		) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,)
				)
				exists = cur.fetchone()
				if not exists:
					cur.execute(
						sql.SQL("CREATE DATABASE {}").format(
							sql.Identifier(self.db_name)
						)
					)
					print(f"Database '{self.db_name}' created.")
				else:
					print(f"Database '{self.db_name}' already exists.")

		# Step 2: Connect to the reddit_data DB
		self.conn = psycopg.connect(
			dbname=self.db_name, user=self.user, host=self.host, port=self.port
		)
		self.cur = self.conn.cursor()

		# Step 3: Create tables if not exist
		self._create_tables()

	def _create_tables(self):
		self.cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS "User" (
				user_id TEXT PRIMARY KEY,
				user_name TEXT NOT NULL
			);
		"""
		)
		self.cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS "Post" (
				post_id TEXT PRIMARY KEY,
				author_id TEXT REFERENCES "User"(user_id),
				title TEXT NOT NULL,
				content TEXT,
				upvotes INTEGER DEFAULT 0
			);
		"""
		)
		self.cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS "Comment" (
				comment_id TEXT PRIMARY KEY,
				author_id TEXT REFERENCES "User"(user_id),
				post_id TEXT REFERENCES "Post"(post_id),
				content TEXT NOT NULL,
				upvotes INTEGER DEFAULT 0
			);
		"""
		)
		self.conn.commit()
		print("Tables ensured.")

	def add_user(self, user_id: str, user_name: str):
		self.cur.execute(
			"""
			INSERT INTO "User" (user_id, user_name)
			VALUES (%s, %s)
			ON CONFLICT (user_id) DO NOTHING;
		""",
			(user_id, user_name),
		)
		self.conn.commit()

	def add_post(
		self, post_id: str, author_id: str, title: str, content: str, upvotes: int = 0
	):
		self.cur.execute(
			"""
			INSERT INTO "Post" (post_id, author_id, title, content, upvotes)
			VALUES (%s, %s, %s, %s, %s)
			ON CONFLICT (post_id) DO NOTHING;
		""",
			(post_id, author_id, title, content, upvotes),
		)
		self.conn.commit()

	def add_comment(
		self,
		comment_id: str,
		author_id: str,
		post_id: str,
		content: str,
		upvotes: int = 0,
	):
		self.cur.execute(
			"""
			INSERT INTO "Comment" (comment_id, author_id, post_id, content, upvotes)
			VALUES (%s, %s, %s, %s, %s)
			ON CONFLICT (comment_id) DO NOTHING;
		""",
			(comment_id, author_id, post_id, content, upvotes),
		)
		self.conn.commit()

	def get_user(self, user_id: str):
		self.cur.execute("""SELECT * FROM "User" WHERE user_id = %s""", (user_id,))
		return self.cur.fetchone()

	def get_users(self):
		self.cur.execute("""SELECT * FROM "User";""")
		return self.cur.fetchall()

	def get_post(self, post_id: str):
		self.cur.execute("""SELECT * FROM "Post" WHERE post_id = %s""", (post_id,))
		return self.cur.fetchone()

	def get_posts(self):
		self.cur.execute("""SELECT * FROM "Post";""")
		return self.cur.fetchall()

	def get_comment(self, comment_id: str):
		self.cur.execute(
			"""SELECT * FROM "Comment" WHERE comment_id = %s""", (comment_id,)
		)
		return self.cur.fetchone()

	def get_comments(self):
		self.cur.execute("""SELECT * FROM "Comment";""")
		return self.cur.fetchall()

	def __del__(self):
		if hasattr(self, "cur") and self.cur:
			self.cur.close()
		if hasattr(self, "conn") and self.conn:
			self.conn.close()
		print("Connection closed.")

class User:
	def __init__(self, id, name):
		self.id = id
		self.name = name

	def __eq__(self, other):
		return isinstance(other, User) and self.id == other.id
	
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return hash(self.id)

class Post:
	def __init__(self, id, author_id, title, content, upvotes):
		self.id = id
		self.author_id = author_id
		self.title = title
		self.content = content
		self.upvotes = upvotes

	def __eq__(self, other):
		return isinstance(other, Post) and self.id == other.id
	
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return hash(self.id)

class Comment:
	def __init__(self, id, author_id, post_id, content, upvotes):
		self.id = id
		self.author_id = author_id
		self.post_id = post_id
		self.content = content
		self.upvotes = upvotes
		
	def __eq__(self, other):
		return isinstance(other, Comment) and self.id == other.id
	
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return hash(self.id)

users = {}
posts = {}
comments = {}

def add_user(u):
	if u.fullname in users:
		return
	
	user = User(u.fullname, u.name)

	print ("Added user " + user.name + " (id " + user.id + ")")
	users[user.id] = user
	db.add_user(user.id, user.name)

def add_post(s):
	if s.name in posts:
		return
	
	post = Post(s.name, s.author.fullname, s.title, s.url if not s.selftext else s.selftext, s.score)

	add_user(s.author)
	print ("Added post " + post.id + " by " + post.author_id + ": \"" + post.title + "\" content " + post.content)
	posts[post.id] = post
	db.add_post(post.id, post.author_id, post.title, post.content, post.upvotes)

def add_comment(c):
	if c.name in comments:
		return
	
	comment = Comment(c.name, c.author.fullname, c.parent_id, c.body, c.score)

	add_user(c.author)
	add_post(reddit.submission(c.parent_id[3:]))

	print ("Added comment on post " + comment.post_id + " by " + comment.author_id + " content " + comment.content)
	comments[comment.id] = comment
	db.add_comment(comment.id, comment.author_id, comment.post_id, comment.content, comment.upvotes)

def treat_user(u, depth, n_posts = 3):
	if depth < 0:
		return

	if not hasattr(u, "fullname"):
		return

	add_user(u)

	for s in u.submissions.top(limit = n_posts):
		treat_submission(s, depth - 1)

def treat_submission(s, depth, n_comments = 3):
	if depth < 0:
		return
	
	print ("hi")

	add_post(s)

	# print ("Post has", len(s.comments), "comments")
	for i in range(min(n_comments, len(s.comments))):
		treat_comment(s.comments[i], depth - 1)

def treat_comment(c, depth):
	if depth < 0:
		return
	
	if not c.parent_id.startswith("t3_"):
		print ("WARNING: treating non-top comment")
		return
	
	if isinstance(c, praw.models.MoreComments) or c.author == None or not hasattr(c.author, "fullname"):
		return
	
	add_comment(c)

	treat_user(c.author, depth - 1)

reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")

r_news = reddit.subreddit("news")

if __name__ == "__main__":
	db = RedditDB()
	
	for p in reddit.subreddit("news").controversial(time_filter = "year"):
		treat_submission(reddit.submission(url="https://www.reddit.com/r/news/comments/1jrzecd/elon_musks_doge_teams_cut_critical_funding_from/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button"), 2)

	# vérifier que les ids sont cohérents (ajouter les user id & les author id avant de les utiliser)
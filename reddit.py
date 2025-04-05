import praw

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
	def __init__(self, id, author_id, title, content):
		self.id = id
		self.author_id = author_id
		self.title = title
		self.content = content

	def __eq__(self, other):
		return isinstance(other, Post) and self.id == other.id
	
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return hash(self.id)

class Comment:
	def __init__(self, id, author_id, post_id, content):
		self.id = id
		self.author_id = author_id
		self.post_id = post_id
		self.content = content
		
	def __eq__(self, other):
		return isinstance(other, Comment) and self.id == other.id
	
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return hash(self.id)

users = set()
posts = set()
comments = set()

def add_user(user):
	print ("Added user " + user.name + " (id " + user.id + ")")
	users.add(user)

def add_post(post):
	print ("Added post " + post.id + " by " + post.author_id + ": \"" + post.title + "\" content " + post.content)
	posts.add(post)

def add_comment(comment):
	print ("Added comment on post " + comment.post_id + " by " + comment.author_id + " content " + comment.content)
	comments.add(comment)

def treat_user(u, depth, n_posts = 3):
	if depth < 0:
		return
	
	if not hasattr(u, "fullname"):
		return
	user = User(u.fullname, u.name)

	if user not in users:
		add_user(user)

	for s in u.submissions.top(limit = n_posts):
		treat_submission(s, depth - 1)

def treat_submission(s, depth, n_comments = 3):
	if depth < 0:
		return
	
	post = Post(s.name, s.author.fullname, s.title, s.url if not s.selftext else s.selftext)

	if post not in posts:
		add_post(post)

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
	
	comment = Comment(c.name, c.author.fullname, c.parent_id, c.body)

	if comment not in comments:
		add_comment(comment)

	treat_user(c.author, depth - 1)


reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")

r_news = reddit.subreddit("news")

treat_submission(reddit.submission(url="https://www.reddit.com/r/news/comments/1jrzecd/elon_musks_doge_teams_cut_critical_funding_from/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button"), 4)
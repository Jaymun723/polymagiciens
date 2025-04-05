import praw
import psycopg
from psycopg import sql
from pg_reddit_driver import RedditDB

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

    print("Added user " + user.name + " (id " + user.id + ")")
    users[user.id] = user
    db.add_user(user.id, user.name)


def add_post(s):
    if s.name in posts:
        return
    
    if s.author == None:
        return

    post = Post(
        s.name,
        s.author.fullname,
        s.title,
        s.url if not s.selftext else s.selftext,
        s.score,
    )

    add_user(s.author)
    print(
        "Added post "
        + post.id
        + " by "
        + post.author_id
        + ': "'
        + post.title
        + '" content '
        + post.content
    )
    posts[post.id] = post
    db.add_post(post.id, post.author_id, post.title, post.content, post.upvotes)


def add_comment(c):
    if c.name in comments:
        return

    if c.author == None:
        return
    
    comment = Comment(c.name, c.author.fullname, c.parent_id, c.body, c.score)

    add_user(c.author)
    add_post(reddit.submission(c.parent_id[3:]))

    print(
        "Added comment on post "
        + comment.post_id
        + " by "
        + comment.author_id
        + " content "
        + comment.content
    )
    comments[comment.id] = comment
    db.add_comment(
        comment.id, comment.author_id, comment.post_id, comment.content, comment.upvotes
    )


def treat_user(u, depth, n_posts=3):
    if depth < 0:
        return

    if not hasattr(u, "fullname"):
        return

    add_user(u)

    for s in u.submissions.top(limit=n_posts):
        treat_submission(s, depth - 1)


def treat_submission(s, depth, n_comments=3):
    if depth < 0:
        return

    print("Post with", len(s.comments), "named", s.title)

    add_post(s)

    # print ("Post has", len(s.comments), "comments")
    for i in range(min(n_comments, len(s.comments))):
        treat_comment(s.comments[i], depth - 1)


def treat_comment(c, depth):
    if depth < 0:
        return

    if not c.parent_id.startswith("t3_"):
        print("WARNING: treating non-top comment")
        return

    if (
        isinstance(c, praw.models.MoreComments)
        or c.author == None
        or not hasattr(c.author, "fullname")
    ):
        return

    add_comment(c)

    treat_user(c.author, depth - 1)

def scrap_post(id):
    treat_submission(reddit.submission(id[3:]), 2)


reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")

# r_news = reddit.subreddit("news")

if __name__ == "__main__":
    db = RedditDB()

    for p in reddit.subreddit("news").controversial(time_filter="year"):
        treat_submission(p, 2)

    # vérifier que les ids sont cohérents (ajouter les user id & les author id avant de les utiliser)

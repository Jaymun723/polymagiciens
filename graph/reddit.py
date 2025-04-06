# import asyncpraw
import praw
import psycopg
from psycopg import sql
from graph.pg_reddit_driver import RedditDB

import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict


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
    def __init__(self, id, author_id, title, content, upvotes, subreddit):
        self.post_id = id
        self.id = id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.upvotes = upvotes
        self.subreddit = subreddit

    def asdict(self):
        return {
            "post_id": self.id,
            "author_id": self.author_id,
            "title": self.title,
            "content": self.content,
            "upvotes": self.upvotes,
            "subreddit": self.subreddit,
        }

    def __eq__(self, other):
        return isinstance(other, Post) and self.post_id == other.post_id

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


class RedditWrapper:
    def __init__(self, db: RedditDB, reddit):
        self.db = db
        self.reddit = reddit

        self.users_set = {}
        self.posts_set = {}
        self.comments_set = {}

    def add_user(self, u):
        if not hasattr(u, "id"):
            return

        if u.id in self.users_set:
            return
        else:
            self.users_set[u.id] = u.id

        user = User(u.id, u.name)

        self.db.add_user(user.id, user.name)

    def add_post(self, p):
        if not p.author:
            return

        if p.id in self.posts_set:
            return
        else:
            self.posts_set[p.id] = p.id

        post = Post(
            p.id,
            p.author.id,
            p.title,
            p.url if not p.selftext else p.selftext,
            p.score,
            p.subreddit.display_name,
        )

        self.add_user(p.author)
        self.db.add_post(
            post.id,
            post.author_id,
            post.title,
            post.content,
            post.subreddit,
            post.upvotes,
        )

    def add_comment(self, c):
        if not c.author:
            return

        if not hasattr(c.author, "id"):
            return

        if c.id in self.comments_set:
            return
        else:
            self.comments_set[c.id] = c.id

        comment = Comment(
            c.id,
            c.author.id,
            c.parent_id[3:],
            c.body,
            c.score,
        )

        self.add_user(c.author)
        # self.add_post(self.reddit.submission(c.parent_id[3:]))

        self.db.add_comment(
            comment.id,
            comment.author_id,
            comment.post_id,
            comment.content,
            comment.upvotes,
        )

    def treat_user(self, u, depth, n_posts=100):
        if depth < 0:
            return

        if not u:
            return

        self.add_user(u)

        for s in u.submissions.top(limit=n_posts):
            print(f"Treating submission: {s.id}")
            self.treat_submission(s, depth - 1)

    def treat_submission(self, s, depth, n_comments=100, save_post=True):
        if depth < 0:
            return

        if save_post:
            self.add_post(s)

        for i in range(min(n_comments, len(s.comments))):
            print(f"Treating comment: {s.comments[i].id}")
            self.treat_comment(s.comments[i], depth - 1)

    def treat_comment(self, c, depth):
        if depth < 0:
            return

        if not c.parent_id.startswith("t3_"):
            print("WARNING: treating non-top comment")
            return

        if isinstance(c, praw.models.MoreComments):
            return

        self.add_comment(c)

        if c.author:
            if hasattr(c.author, "id"):
                print(f"Treating user: {c.author.id}")
                self.treat_user(c.author, depth - 1)

import asyncpraw
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


# def add_user(u):
#     if u.fullname in users:
#         return

#     user = User(u.fullname, u.name)

#     print("Added user " + user.name + " (id " + user.id + ")")
#     users[user.id] = user
#     db.add_user(user.id, user.name)


# def add_post(s):
#     if s.name in posts:
#         return


#     post = Post(
#         s.name,
#         s.author.fullname if s.author.fullname else "anonymous",
#         s.title,
#         s.url if not s.selftext else s.selftext,
#         s.score,
#     )
def add_post(s):
    if s.name in posts:
        return

    post = Post(
        s.name,
        s.author.fullname if s.author.fullname else "anonymous",
        s.title,
        s.url if not s.selftext else s.selftext,
        s.score,
    )


#     add_user(s.author)
#     print(
#         "Added post "
#         + post.id
#         + " by "
#         + post.author_id
#         + ': "'
#         + post.title
#         + '" content '
#         + post.content
#     )
#     posts[post.id] = post
#     db.add_post(post.id, post.author_id, post.title, post.content, post.upvotes)


# def add_comment(c):
#     if c.name in comments:
#         return


#     comment = Comment(c.name, c.author.fullname if c.author.fullname else "anonymous", c.parent_id, c.body, c.score)
def add_comment(c):
    if c.name in comments:
        return

    comment = Comment(
        c.name,
        c.author.fullname if c.author.fullname else "anonymous",
        c.parent_id,
        c.body,
        c.score,
    )


#     add_user(c.author)
#     add_post(reddit.submission(c.parent_id[3:]))

#     print(
#         "Added comment on post "
#         + comment.post_id
#         + " by "
#         + comment.author_id
#         + " content "
#         + comment.content
#     )
#     comments[comment.id] = comment
#     db.add_comment(
#         comment.id, comment.author_id, comment.post_id, comment.content, comment.upvotes
#     )


# def treat_user(u, depth, n_posts=3):
#     if depth < 0:
#         return

#     if not hasattr(u, "fullname"):
#         u.fullname = "anonymous"

#     add_user(u)

#     for s in u.submissions.top(limit=n_posts):
#         treat_submission(s, depth - 1)


# def treat_submission(s, depth, n_comments=3):
#     if depth < 0:
#         return

#     print("Post with", len(s.comments), "named", s.title)

#     add_post(s)

#     # print ("Post has", len(s.comments), "comments")
#     for i in range(min(n_comments, len(s.comments))):
#         treat_comment(s.comments[i], depth - 1)


# def treat_comment(c, depth):
#     if depth < 0:
#         return

#     if not c.parent_id.startswith("t3_"):
#         print("WARNING: treating non-top comment")
#         return

#     if (
#         isinstance(c, praw.models.MoreComments)
#     ):
#         return

#     add_comment(c)

#     treat_user(c.author, depth - 1)


class RedditScraper:
    def __init__(self, reddit, db, max_workers=10):
        self.reddit = reddit
        self.db = db
        self.users = {}
        self.posts = {}
        self.comments = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def add_user(self, u):
        await u.load()
        if u.fullname in self.users:
            return
        user = User(u.fullname, u.name)
        self.users[user.id] = user
        print(f"Added user {user.name} (id {user.id})")
        self.db.add_user(user.id, user.name)

    async def add_post(self, s):
        await s.load()
        if s.name in self.posts:
            return
        author_id = (
            s.author.fullname
            if s.author and hasattr(s.author, "fullname")
            else "anonymous"
        )
        post = Post(
            s.name, author_id, s.title, s.url if not s.selftext else s.selftext, s.score
        )
        await self.add_user(s.author)
        self.posts[post.id] = post
        print(
            f'Added post {post.id} by {post.author_id}: "{post.title}" content {post.content}'
        )
        self.db.add_post(
            post.id, post.author_id, post.title, post.content, post.upvotes
        )

    async def add_comment(self, c):
        await c.load()
        if c.name in self.comments:
            return
        author_id = (
            c.author.fullname
            if c.author and hasattr(c.author, "fullname")
            else "anonymous"
        )
        comment = Comment(c.name, author_id, c.parent_id, c.body, c.score)
        await self.add_user(c.author)
        post_id = c.parent_id[3:]
        sub = await self.reddit.submission(post_id)
        await self.add_post(sub)
        print(
            f"Added comment on post {comment.post_id} by {comment.author_id} content {comment.content}"
        )
        self.comments[comment.id] = comment
        self.db.add_comment(
            comment.id,
            comment.author_id,
            comment.post_id,
            comment.content,
            comment.upvotes,
        )

    def _treat_user_sync(self, u, depth, n_posts=3):
        if depth < 0:
            return
        if not hasattr(u, "fullname"):
            u.fullname = "anonymous"
        self.add_user(u)
        for s in u.submissions.top(limit=n_posts):
            self._treat_submission_sync(s, depth - 1)

    def _treat_submission_sync(self, s, depth, n_comments=3):
        if depth < 0:
            return
        print("Post with", len(s.comments), "named", s.title)
        self.add_post(s)
        for i in range(min(n_comments, len(s.comments))):
            self._treat_comment_sync(s.comments[i], depth - 1)

    def _treat_comment_sync(self, c, depth):
        if (
            depth < 0
            or not c.parent_id.startswith("t3_")
            or isinstance(c, asyncpraw.models.MoreComments)
        ):
            return
        self.add_comment(c)
        self._treat_user_sync(c.author, depth - 1)

    async def treat_user(self, u, depth=1, n_posts=3):
        await asyncio.get_running_loop().run_in_executor(
            self.executor, self._treat_user_sync, u, depth, n_posts
        )

    async def treat_submission(self, s, depth=1, n_comments=3):
        await asyncio.get_running_loop().run_in_executor(
            self.executor, self._treat_submission_sync, s, depth, n_comments
        )

    async def treat_comment(self, c, depth=1):
        await asyncio.get_running_loop().run_in_executor(
            self.executor, self._treat_comment_sync, c, depth
        )


# def scrap_post(id):
#     treat_submission(reddit.submission(id[3:]), 2)


def treat_comment(c, depth):
    if depth < 0:
        return

    if not c.parent_id.startswith("t3_"):
        print("WARNING: treating non-top comment")
        return

    if isinstance(c, praw.models.MoreComments):
        return

    add_comment(c)

    treat_user(c.author, depth - 1)


def scrap_post(id):
    treat_submission(reddit.submission(id[3:]), 2)


reddit = praw.Reddit("bot1", user_agent="polymagiciens bot1")

# r_news = reddit.subreddit("news")


async def main():
    db = RedditDB()

    reddit = asyncpraw.Reddit("bot1", user_agent="polymagiciens bot1")
    s = RedditScraper(reddit, db)

    sub = await reddit.subreddit("news")

    async for p in sub.controversial(time_filter="year"):
        await s.treat_submission(p, 2)

    # vérifier que les ids sont cohérents (ajouter les user id & les author id avant de les utiliser)


if __name__ == "__main__":
    asyncio.run(main())

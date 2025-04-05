import asyncpraw
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


class RedditWrapper:
    def __init__(self, db: RedditDB, reddit):
        self.db = db
        self.reddit = reddit

    def add_user(self, u):
        if not hasattr(u, "id"):
            return

        user = User(u.id, u.name)

        print("Added user " + user.name + " (id " + user.id + ")")
        self.db.add_user(user.id, user.name)

    def add_post(self, p):
        post = Post(
            p.id,
            p.author.id,
            p.title,
            p.url if not p.selftext else p.selftext,
            p.score,
        )

        self.add_user(p.author)
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
        self.db.add_post(
            post.id, post.author_id, post.title, post.content, post.upvotes
        )

    def add_comment(self, c):
        if not c.author:
            return

        if not hasattr(c.author, "id"):
            return

        comment = Comment(
            c.id,
            c.author.id,
            c.parent_id,
            c.body,
            c.score,
        )

        self.add_user(c.author)
        self.add_post(self.reddit.submission(c.parent_id[3:]))

        print(
            "Added comment on post "
            + comment.post_id
            + " by "
            + comment.author_id
            + " content "
            + comment.content
        )
        self.db.add_comment(
            comment.id,
            comment.author_id,
            comment.post_id,
            comment.content,
            comment.upvotes,
        )

    def treat_user(self, u, depth, n_posts=3):
        if depth < 0:
            return

        if not u:
            return

        self.add_user(u)

        for s in u.submissions.top(limit=n_posts):
            self.treat_submission(s, depth - 1)

    def treat_submission(self, s, depth, n_comments=3):
        if depth < 0:
            return

        # print("Post with", len(s.comments), "named", s.title)

        self.add_post(s)

        # print ("Post has", len(s.comments), "comments")
        for i in range(min(n_comments, len(s.comments))):
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

        self.treat_user(c.author, depth - 1)


class RedditScraper:
    def __init__(self, reddit, db, max_workers=10):
        self.reddit = reddit
        self.db = db
        self.users = {}
        self.posts = {}
        self.comments = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.post_queue = asyncio.Queue()
        self.comment_queue = asyncio.Queue()
        self.user_queue = asyncio.Queue()

        user = User("anonymous", "anonymous")
        self.users[user.id] = user
        print(f"Added user {user.name} (id {user.id})")
        self.db.add_user(user.id, user.name)

    async def run(self, initial_users, depth=1, n_posts=3, n_comments=3):
        for user in initial_users:
            await self.user_queue.put((user, depth))

        tasks = [
            asyncio.create_task(self.worker(n_posts, n_comments)) for _ in range(5)
        ]
        await self.user_queue.join()
        await self.post_queue.join()
        await self.comment_queue.join()

        for t in tasks:
            t.cancel()

    async def worker(self):
        try:
            while True:
                if not self.user_queue.empty():
                    user, depth = await self.user_queue.get()
                    await self.treat_user(user, depth)
                    self.user_queue.task_done()
                elif not self.post_queue.empty():
                    submission, depth = await self.post_queue.get()
                    await self.treat_submission(submission, depth)
                    self.post_queue.task_done()
                elif not self.comment_queue.empty():
                    comment, depth = await self.comment_queue.get()
                    await self.treat_comment(comment, depth)
                    self.comment_queue.task_done()
                else:
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

    async def treat_user(self, user, depth, n_posts=3):
        await self.add_user(user)
        if depth < 0:
            return
        async for submission in user.submissions.top(limit=n_posts):
            await self.post_queue.put((submission, depth - 1))

    async def treat_submission(self, submission, depth, n_comments=3):
        await self.add_post(submission)
        if depth < 0:
            return
        await submission.load()
        await submission.comments.replace_more(limit=0)
        for i, comment in enumerate(submission.comments[:n_comments]):
            await self.comment_queue.put((comment, depth - 1))

    async def treat_comment(self, comment, depth):
        if not comment.parent_id.startswith("t3_"):  # Not a top-level comment
            return
        await self.add_comment(comment)
        if depth < 0:
            return
        if comment.author:
            await self.user_queue.put((comment.author, depth - 1))

    async def add_user(self, u):
        if u is None:
            return
        await u.load()
        if hasattr(u, "fullname") and u.fullname in self.users:
            return

        user = User(
            u.fullname if hasattr(u, "fullname") else "anonymous",
            u.name if hasattr(u, "name") else "anonymous",
        )
        self.users[user.id] = user
        print(f"Added user {user.name} (id {user.id})")
        await asyncio.get_running_loop().run_in_executor(
            self.executor, self.db.add_user, user.id, user.name
        )

    async def add_post(self, s):
        await s.load()
        if s.name in self.posts:
            return
        author_id = (
            s.author.fullname
            if s.author and hasattr(s.author, "fullname")
            else "anonymous"
        )
        content = s.url if not s.selftext else s.selftext
        post = Post(s.name, author_id, s.title, content, s.score)
        await self.add_user(s.author)
        self.posts[post.id] = post
        print(
            f'Added post {post.id} by {post.author_id}: "{post.title}" content {post.content}'
        )
        await asyncio.get_running_loop().run_in_executor(
            self.executor,
            self.db.add_post,
            post.id,
            post.author_id,
            post.title,
            post.content,
            post.upvotes,
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
        self.comments[comment.id] = comment
        print(
            f"Added comment on post {comment.post_id} by {comment.author_id} content {comment.content}"
        )
        await asyncio.get_running_loop().run_in_executor(
            self.executor,
            self.db.add_comment,
            comment.id,
            comment.author_id,
            comment.post_id,
            comment.content,
            comment.upvotes,
        )


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

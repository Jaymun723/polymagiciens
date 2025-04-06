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
                user_name TEXT NOT NULL,
                score INTEGER DEFAULT 50 CHECK (score BETWEEN 0 AND 100)
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
                subreddit TEXT NOT NULL,
                upvotes INTEGER DEFAULT 0,
                score INTEGER DEFAULT 50 CHECK (score BETWEEN 0 AND 100),
                treated BOOLEAN DEFAULT FALSE,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                upvotes INTEGER DEFAULT 0,
                score INTEGER DEFAULT 50 CHECK (score BETWEEN 0 AND 100),
                treated BOOLEAN DEFAULT FALSE,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        self.conn.commit()
        print("Tables ensured.")

    def add_user(self, user_id: str, user_name: str, score: int = 50):
        print(
            f"Inserted: User(user_di={user_id}, user_name={user_name}, score={score})"
        )
        self.cur.execute(
            """
            INSERT INTO "User" (user_id, user_name, score)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING;
        """,
            (user_id, user_name, score),
        )
        self.conn.commit()

    # def add_post(
    #     self,
    #     post_id: str,
    #     author_id: str,
    #     title: str,
    #     content: str,
    #     subreddit: str,
    #     upvotes: int = 0,
    #     score: int = 0,
    #     treated: bool = False,
    #     date=None,
    # ):
    #     self.cur.execute(
    #         """INSERT INTO "Post" (post_id, author_id, title, content, upvotes, subreddit)
    #         VALUES (%(post_id)s, %(author_id)s, %(title)s, %(content)s, %(upvotes)s, %(subreddit)s)
    #         ON CONFLICT (post_id) DO NOTHING;""",
    #         {
    #             "post_id": post_id,
    #             "author_id": author_id,
    #             "title": title,
    #             "content": content,
    #             "upvotes": upvotes,
    #             "subreddit": subreddit,
    #         },
    #     )
    #     self.conn.commit()

    def add_post(
        self,
        post_id: str,
        author_id: str,
        title: str,
        content: str,
        subreddit: str,
        upvotes: int = 0,
        score: int = 50,
        treated: bool = False,
        date=None,
    ):
        print(
            f"Inserted: Post(post_id={post_id}, author_id={author_id}, title={title}, content={content}, subreddit={subreddit}, upvotes={upvotes}, score={score}, treated={treated}, date={date})"
        )
        self.cur.execute(
            """
            INSERT INTO "Post" (
                post_id, author_id, title, content, subreddit,
                upvotes, score, treated, date
            )
            VALUES (
                %(post_id)s, %(author_id)s, %(title)s, %(content)s, %(subreddit)s,
                %(upvotes)s, %(score)s, %(treated)s, COALESCE(%(date)s, CURRENT_TIMESTAMP)
            )
            ON CONFLICT (post_id) DO NOTHING;
            """,
            {
                "post_id": post_id,
                "author_id": author_id,
                "title": title,
                "content": content,
                "subreddit": subreddit,
                "upvotes": upvotes,
                "score": score,
                "treated": treated,
                "date": date,
            },
        )
        self.conn.commit()

    def add_comment(
        self,
        comment_id: str,
        author_id: str,
        post_id: str,
        content: str,
        upvotes: int = 0,
        score: int = 50,
        treated: bool = False,
        date=None,
    ):
        print(
            f"Inserted: Comment(comment_id={comment_id},author_id={author_id},post_id={post_id},content={content},upvotes={upvotes},score={score},treated={treated},date={date})"
        )
        self.cur.execute(
            """
            INSERT INTO "Comment" (
                comment_id, author_id, post_id, content,
                upvotes, score, treated, date
            )
            VALUES (
                %(comment_id)s, %(author_id)s, %(post_id)s, %(content)s,
                %(upvotes)s, %(score)s, %(treated)s, COALESCE(%(date)s, CURRENT_TIMESTAMP)
            )
            ON CONFLICT (comment_id) DO NOTHING;
            """,
            {
                "comment_id": comment_id,
                "author_id": author_id,
                "post_id": post_id,
                "content": content,
                "upvotes": upvotes,
                "score": score,
                "treated": treated,
                "date": date,
            },
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

    def get_treated_posts(self):
        self.cur.execute(
            """
            SELECT * FROM "Post"
            WHERE treated = TRUE;
        """
        )
        return self.cur.fetchall()

    def mark_post_as_treated(self, post_id: str):
        self.cur.execute(
            """
            UPDATE "Post"
            SET treated = TRUE
            WHERE post_id = %s;
        """,
            (post_id,),
        )
        self.conn.commit()

    def update_post_score(self, post_id: str, new_score: int):
        self.cur.execute(
            """
            UPDATE "Post"
            SET score = %s
            WHERE post_id = %s;
        """,
            (new_score, post_id),
        )
        self.conn.commit()

    def update_comment_score(self, comment_id: str, new_score: int):
        self.cur.execute(
            """
            UPDATE "Comment"
            SET score = %s, treated = TRUE
            WHERE comment_id = %s;
        """,
            (new_score, comment_id),
        )
        self.conn.commit()

    def get_treated_posts_ordered_by_comments(self):
        self.cur.execute(
            """
            SELECT p.*, COUNT(c.comment_id) AS comment_count
            FROM "Post" p
            LEFT JOIN "Comment" c ON p.post_id = c.post_id
            WHERE p.treated = TRUE
            GROUP BY p.post_id
            ORDER BY comment_count DESC;
        """
        )
        return self.cur.fetchall()

    def get_comments_by_post_id(self, post_id: str):
        self.cur.execute(
            """
            SELECT * FROM "Comment"
            WHERE post_id = %s AND treated = FALSE;
        """,
            (post_id,),
        )
        return self.cur.fetchall()

    def get_most_commented_unprocessed_post(self, limit=1):
        self.cur.execute(
            """SELECT p.*
            FROM "Post" p
            LEFT JOIN "Comment" c ON p.post_id = c.post_id
            WHERE p.treated = FALSE
            GROUP BY p.post_id
            ORDER BY COUNT(c.comment_id) DESC
            LIMIT %s;""",
            (limit,),
        )
        return self.cur.fetchall()

    def get_posts(self):
        self.cur.execute("""SELECT * FROM "Post";""")
        return self.cur.fetchall()

    def post_exists(self, post_id: str) -> bool:
        self.cur.execute(
            """SELECT 1 FROM "Post" WHERE post_id = %s;""",
            (post_id,),
        )
        return self.cur.fetchone() is not None

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


if __name__ == "__main__":
    db = RedditDB()

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


if __name__ == "__main__":
    db = RedditDB()
    # db.add_user("u1", "alice")
    # db.add_post("p1", "u1", "First Post", "This is content", 12)
    # db.add_comment("c1", "u1", "p1", "Nice one!", 3)

    # print(db.get_user("u1"))
    # print(db.get_users())

    # print(db.get_post("p1"))
    # print(db.get_posts())

    # print(db.get_comment("c1"))
    print(db.get_users())

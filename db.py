import psycopg2
import time

class DBClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self.conn = None

    def connect(self, retries=10, delay=2):
        for attempt in range(1, retries + 1):
            try:
                self.conn = psycopg2.connect(
                    host=self.cfg["host"],
                    port=self.cfg["port"],
                    dbname=self.cfg["database"],
                    user=self.cfg["user"],
                    password=self.cfg["password"],
                    connect_timeout=5
                )
                self.conn.autocommit = True
                return
            except psycopg2.OperationalError as e:
                if attempt == retries:
                    raise
                print(
                    f"⏳ DB not ready ({self.cfg['host']}), retry {attempt}/{retries}"
                )
                time.sleep(delay)

    def query(self, sql):
        with self.conn.cursor() as cur:
            cur.execute(sql)
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return []

    def close(self):
        if self.conn:
            self.conn.close()

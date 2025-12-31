class PublicationManager:
    def __init__(self, db, pub, tables):
        self.db = db
        self.pub = pub
        self.tables = set(tables)

    def reconcile(self):
        if not self._exists():
            self.db.query(
                f"CREATE PUBLICATION {self.pub} FOR TABLE {', '.join(self.tables)}"
            )
        self._add_missing()

    def _exists(self):
        return bool(
            self.db.query(
                f"SELECT 1 FROM pg_publication WHERE pubname='{self.pub}'"
            )
        )

    def _add_missing(self):
        existing = {
            r[0] for r in self.db.query(
                f"""
                SELECT schemaname||'.'||tablename
                FROM pg_publication_tables
                WHERE pubname='{self.pub}'
                """
            )
        }
        for t in self.tables - existing:
            self.db.query(f"ALTER PUBLICATION {self.pub} ADD TABLE {t}")

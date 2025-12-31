class SchemaValidator:
    def __init__(self, source, target, tables):
        self.source = source
        self.target = target
        self.tables = tables

    def validate(self):
        for table in self.tables:
            if self._columns(table, self.source) != self._columns(table, self.target):
                raise Exception(f"Schema mismatch for {table}")

    def _columns(self, table, db):
        schema, name = table.split(".")
        return db.query(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema='{schema}'
              AND table_name='{name}'
            ORDER BY ordinal_position;
        """)

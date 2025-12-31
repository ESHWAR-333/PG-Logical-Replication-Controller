class SubscriptionManager:
    def __init__(self, db, cfg):
        self.db = db
        self.cfg = cfg

    def exists(self):
        name = self.cfg["subscription"]["name"]
        return bool(
            self.db.query(
                f"SELECT 1 FROM pg_subscription WHERE subname='{name}'"
            )
        )

    def reconcile(self):
        name = self.cfg["subscription"]["name"]

        if self.exists():
            print(f"⏭ Subscription {name} already exists")
            return

        src = self.cfg["source"]
        pub = self.cfg["publication"]["name"]

        same_instance = (
            src["host"] == self.cfg["target"]["host"]
            and src["port"] == self.cfg["target"]["port"]
        )

        if same_instance:
            self._create_same_instance(name, pub)
        else:
            self._create_cross_instance(name, pub)

    def _create_same_instance(self, name, pub):
        src = self.cfg["source"]
        conn = (
            f"host={src['host']} port={src['port']} "
            f"dbname={src['database']} user={src['user']} "
            f"password={src['password']}"
        )

        self.db.query(f"""
            CREATE SUBSCRIPTION {name}
            CONNECTION '{conn}'
            PUBLICATION {pub}
            WITH (
              slot_name = '{name}',
              create_slot = false,
              copy_data = true
            );
        """)

        print(f"🔗 Created subscription {name} (same instance)")

    def _create_cross_instance(self, name, pub):
        src = self.cfg["source"]
        conn = (
            f"host={src['host']} port={src['port']} "
            f"dbname={src['database']} user={src['user']} "
            f"password={src['password']}"
        )

        self.db.query(f"""
            CREATE SUBSCRIPTION {name}
            CONNECTION '{conn}'
            PUBLICATION {pub}
            WITH (copy_data = true);
        """)

        print(f"🔗 Created subscription {name} (cross instance)")

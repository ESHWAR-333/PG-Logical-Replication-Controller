from db import DBClient

class PrecheckEngine:
    def __init__(self, cfg):
        self.cfg = cfg

    def run(self):
        db = DBClient(self.cfg["source"])
        db.connect()

        self._check_param(db, "wal_level", "logical")
        self._check_min(db, "max_replication_slots", 1)
        self._check_min(db, "max_wal_senders", 1)

        db.close()

    def _check_param(self, db, name, expected):
        val = db.query(f"SHOW {name};")[0][0]
        if val != expected:
            raise Exception(f"{name} must be {expected}")

    def _check_min(self, db, name, minimum):
        val = int(db.query(f"SHOW {name};")[0][0])
        if val < minimum:
            raise Exception(f"{name} must be >= {minimum}")

    def _ensure_database(self, db_cfg):
        admin_cfg = db_cfg.copy()
        admin_cfg["database"] = "postgres"
    
        admin = DBClient(admin_cfg)
        admin.connect()
    
        exists = admin.query(
            f"SELECT 1 FROM pg_database WHERE datname='{db_cfg['database']}'"
        )
    
        if not exists:
            admin.query(f"CREATE DATABASE {db_cfg['database']}")
            print(f"📀 Created database {db_cfg['database']}")
    
        admin.close()

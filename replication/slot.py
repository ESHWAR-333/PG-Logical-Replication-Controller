class SlotManager:
    def __init__(self, db, slot_name):
        self.db = db
        self.slot = slot_name

    def ensure(self):
        exists = self.db.query(f"""
            SELECT 1
            FROM pg_replication_slots
            WHERE slot_name = '{self.slot}'
        """)
        if not exists:
            self.db.query(
                f"SELECT pg_create_logical_replication_slot('{self.slot}', 'pgoutput')"
            )
            print(f"🔧 Created replication slot {self.slot}")
        else:
            print(f"⏭ Slot {self.slot} already exists")

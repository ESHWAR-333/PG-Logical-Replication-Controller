from config_loader import load_config
from state_store import StateStore
from db import DBClient
from precheck.engine import PrecheckEngine
from schema.validator import SchemaValidator
from replication.slot import SlotManager
from replication.publication import PublicationManager
from replication.subscription import SubscriptionManager


def main():
    config = load_config()
    state = StateStore(config["global"]["state_file"])

    for name, cfg in config["replications"].items():
        print(f"\n🔁 Reconciling {name}")

        # 1. Prechecks
        PrecheckEngine(cfg).run()

        src = DBClient(cfg["source"])
        tgt = DBClient(cfg["target"])
        src.connect()
        tgt.connect()

        # 2. Schema validation
        SchemaValidator(src, tgt, cfg["tables"]).validate()

        # 3. Publication reconciliation
        PublicationManager(
            src,
            cfg["publication"]["name"],
            cfg["tables"]
        ).reconcile()

        # 4. Same-instance detection
        same_instance = (
            cfg["source"]["host"] == cfg["target"]["host"]
            and cfg["source"]["port"] == cfg["target"]["port"]
        )

        # 5. Subscription reconciliation
        sub_mgr = SubscriptionManager(tgt, cfg)

        if same_instance and not sub_mgr.exists():
            # Slot must exist BEFORE subscription
            SlotManager(
                src,
                cfg["subscription"]["name"]
            ).ensure()

        sub_mgr.reconcile()

        # 6. Persist state
        state.update(name, {
            "publication": True,
            "subscription": True
        })

        src.close()
        tgt.close()

        print(f"✅ {name} completed")


if __name__ == "__main__":
    main()

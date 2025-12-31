# 🚀 Logical Replication Controller for PostgreSQL (PG-ReplicaCtl)

### A Config-Driven Logical Replication Controller for PostgreSQL

PG-ReplicaCtl is a **declarative, idempotent control plane** for managing **PostgreSQL Logical Replication**.

It automates the *entire lifecycle* of logical replication using a **single configuration file**, safely reconciling PostgreSQL’s current state with a desired state — without restarts, manual cleanup, or fragile scripts.

This project is intentionally designed to reflect **real production behavior**, not a toy example.

---

## 📌 Why This Project Exists

PostgreSQL logical replication is powerful but operationally fragile:

- Strict prerequisites (`wal_level`, slots, workers)
- Schema must already exist on the target
- Slot behavior differs by topology
- Re-running scripts often leads to:
  - duplicate replication slots
  - WAL bloat
  - broken subscriptions
  - partial setups

**PG-ReplicaCtl solves this by acting as a reconciliation engine.**

> **Config = Desired State**  
> **PostgreSQL = Current State**  
> **Controller = Reconciler**

You can safely re-run it any number of times.

---

## ✨ What PG-ReplicaCtl Does

✅ Validates PostgreSQL logical replication prerequisites  
✅ Ensures databases exist  
✅ Verifies schema compatibility (source vs target)  
✅ Creates and updates publications  
✅ Creates and reconciles subscriptions  
✅ Correctly handles replication slots  
✅ Supports incremental table additions  
✅ Tracks applied state for idempotency  

---

## ❌ What PG-ReplicaCtl Does NOT Do

- ❌ Does not create schemas or tables
- ❌ Does not migrate DDL
- ❌ Does not manage application traffic
- ❌ Does not replace CDC platforms like Debezium

This tool focuses **only** on logical replication orchestration.

---

## 🧠 Core Design Principles

- Databases are **long-running infrastructure**
- Configuration is the **single source of truth**
- Safe to run **multiple times**
- Only **new changes** are applied
- Nothing is blindly recreated
- Same behavior locally and on AWS RDS

---

## 🏗 Supported Replication Topologies

### 1️⃣ Cross-Instance / Cross-Container Replication

```

Postgres A (sales) ─────────▶ Postgres B (sales_replica)

```

- Replication slot is auto-created
- Subscription uses `create_slot = true`
- Standard PostgreSQL logical replication flow

---

### 2️⃣ Same PostgreSQL Instance, Different Databases


```

Postgres Instance
├── hr
└── hr_replica

```

- Replication slot must be **manually created**
- Subscription uses `create_slot = false`
- Prevents slot conflicts and recursive replication
- Required for real PostgreSQL and AWS RDS setups

PG-ReplicaCtl detects this topology and handles it correctly.

---

## ⚙️ How the Controller Works (Step by Step)

For each replication defined in the config file:

1. **Precheck Engine**
   - PostgreSQL connectivity
   - Logical replication settings
   - Database existence

2. **Schema Validator**
   - Tables exist on source and target
   - Column order, types, and nullability match

3. **Publication Reconciliation**
   - Create publication if missing
   - Add only newly configured tables

4. **Replication Slot Handling**
   - Cross-instance: managed by subscription
   - Same-instance: explicitly created

5. **Subscription Reconciliation**
   - Create subscription if missing
   - Skip if already present

6. **State Persistence**
   - Applied state is stored
   - Enables safe, repeatable runs

---

## 📁 Project Structure

```

logical-replication-controller/
│
├── docker-compose.yml # PostgreSQL + controller setup
├── Dockerfile # Controller image
├── replication_config.yaml # Desired replication state
├── .lr_state.json # Controller-managed state file
│
├── main.py # Orchestration entry point
├── config_loader.py
├── state_store.py
├── db.py
│
├── precheck/
│ └── engine.py # Precheck engine
│
├── schema/
│ └── validator.py # Schema validation logic
│
├── replication/
│ ├── publication.py # Publication reconciler
│ ├── subscription.py # Subscription reconciler
│ └── slot.py # Replication slot manager
│
└── README.md


```



---

## 📄 Configuration File (Desired State)

All behavior is driven by **one YAML file**.

Example:

```yaml
global:
  state_file: ".lr_state.json"

replications:
  sales_lr:
    source:
      host: source-db
      port: 5432
      database: sales
      user: repl_user
      password: repl_password

    target:
      host: target-db
      port: 5432
      database: sales_replica
      user: repl_user
      password: repl_password

    publication:
      name: sales_pub

    subscription:
      name: sales_sub
      copy_data: true

    tables:
      - public.orders
      - public.customers
```



## 🔁 Incremental Workflow (No Restart Required)

To add a new table to replication:

1. Create the table in the **source** database  
2. Create the table in the **target** database  
3. Add the table to `replication_config.yaml`  
4. Re-run the controller  

✔ No database restart  
✔ No publication recreation  
✔ No subscription recreation  

Only the **new table** is applied.

---

## 🐳 Local Development with Docker

PostgreSQL containers are treated as **long-running infrastructure** and run continuously.

### Start PostgreSQL (One Time)

```bash
docker compose up -d --build
```

Run the Controller


```
docker compose run --rm lr-tool

```





## 🔐 Security Notes

- Passwords are inline only for local testing
- For real environments:
  - Use environment variables
  - Use AWS Secrets Manager or HashiCorp Vault
- PostgreSQL passwords cannot be retrieved from the database

## ⚠️ Important PostgreSQL Facts

- Logical replication does not replicate schema
- Target tables must exist beforehand
- Replication slots are cluster-wide
- Improper slot cleanup causes WAL retention issues

PG-ReplicaCtl handles these constraints intentionally.

Real-Time GitHub Event Lakehouse & CI/CD Analytics Engine
A production-grade, streaming-to-batch analytical lakehouse pipeline built with Python, DuckDB, dbt Core, and GitHub Actions.

This project demonstrates enterprise data engineering standards, including real-time payload ingestion, append-only semi-structured raw storage, incremental micro-batch parsing, automated data quality testing, and dynamic schema isolation across continuous integration and continuous deployment (CI/CD) workflows.

🏗️ Architecture & Data Flow
+--------------------------+       +------------------------------------+
|  GitHub Live Events API  | ----> |   Python Producer (producer.py)    |
+--------------------------+       +------------------------------------+
                                                     |
                                                     v (Append-Only JSON)
                                   +------------------------------------+
                                   |    DuckDB OLAP Lakehouse Engine    |
                                   |     ('events_lakehouse.duckdb')    |
                                   +------------------------------------+
                                                     |
                                                     v (dbt Transformation)
                                   +------------------------------------+
                                   |       Incremental Staging          |
                                   |      (stg_github_events.sql)       |
                                   +------------------------------------+
                                                     |
                                                     v
                                   +------------------------------------+
                                   |      Daily Business Metrics        |
                                   |   (fct_github_daily_metrics.sql)   |
                                   +------------------------------------+

Ingestion Layer: Python continuous producer polls GitHub's live /events stream API, handling deduplication via primary key constraint assertions (ON CONFLICT DO NOTHING).

Lakehouse Storage Layer: Embedded DuckDB database engine acts as a high-performance local analytical landing zone for raw semi-structured JSON strings.

Transformation Layer: dbt Core models handle JSON extraction, schema enforcement, data typing, and incremental materializations.

Data Governance & Quality: Integrated testing (unique, not_null) guarantees structural integrity at build time.

CI/CD Automation: Automated GitHub Actions workflows orchestrate isolated testing environments for incoming PRs and scheduled production releases.

🧰 Tech Stack
Language: Python 3.12 (requests, duckdb)

Storage & Query Engine: DuckDB

Data Transformation: dbt Core (dbt-duckdb adapter)

Orchestration & CI/CD: GitHub Actions

Version Control: Git & GitHub

📊 Data Models & Transformation Strategy
Staging Layer (stg_github_events.sql)
Materialization: incremental

Unique Key: event_id

Purpose: Parses top-level fields alongside deeply nested JSON payloads (json_extract_string). Employs micro-batch execution filtering where ingested_at > max(ingested_at).

Marts Layer (fct_github_daily_metrics.sql)
Materialization: table / view

Purpose: Aggregates event volumes, unique active contributors, and detailed event breakdowns (pushes, stars, pull requests, issues) truncated by repository and date.

Quality Assertions (schema.yml)
Automated data assertions run on every build to safeguard downstreams against schema drift or missing primary keys:

Primary Key Uniqueness (event_id)

Non-null constraints on mandatory operational dimensions (event_type, repo_name)

🔄 CI/CD & Environment Governance
Pipeline

Trigger

Command

Target Schema

Objective

CI

Pull Request / Commit

dbt build

ci_pr_<id> / ci_commit_<sha>

Builds models in ephemeral, isolated schemas to prevent polluting production data.

CD

PR Merge / Schedule (CRON)

dbt build --target prod

prod

Deploys validated code changes and updates production analytical tables.

🚀 How to Run Locally
1. Prerequisites
Python 3.10+

Git

2. Setup Virtual Environment
git clone (https://github.com/Austinjnrishere/Modern-Lakehouse-Event-Streaming-Pipeline)

python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install requests duckdb dbt-duckdb

3. Run Ingestion Producer
Seed your DuckDB lakehouse with live streaming events:

python producer.py

4. Execute dbt Pipeline
Navigate to the dbt project and run transformations & quality tests:


# Run models locally against dev environment
dbt build

# Inspect interactive lineage DAG and documentation
dbt docs generate
dbt docs serve

🔍 Visualizing Results
The resulting data platform can be queried using:

DuckDB CLI: python -c "import duckdb; duckdb.connect('events_lakehouse.duckdb').shell()"

GUI Tools: Connect DBeaver Community Edition directly to events_lakehouse.duckdb.

SELECT * FROM prod.fct_github_daily_metrics ORDER BY total_events DESC LIMIT 10;

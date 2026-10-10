import json
import time
import duckdb
import requests

# 1. Initialize local DuckDB database file
DB_PATH = "events_lakehouse.duckdb"
conn = duckdb.connect(DB_PATH)

# 2. Create raw append-only landing table
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS raw_github_events (
        event_id VARCHAR PRIMARY KEY,
        event_type VARCHAR,
        actor_login VARCHAR,
        repo_name VARCHAR,
        created_at TIMESTAMP,
        raw_payload VARCHAR,
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)


def fetch_and_ingest_events():
    url = "https://api.github.com/events"
    headers = {"User-Agent": "Analytical-Engineer-Project"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            return

        events = response.json()

        for event in events:
            event_id = str(event.get("id"))
            event_type = event.get("type")
            actor = event.get("actor", {}).get("login")
            repo = event.get("repo", {}).get("name")
            created_at = event.get("created_at")
            raw_payload = json.dumps(event)

            # Insert using ON CONFLICT DO NOTHING to avoid duplicate event IDs
            conn.execute(
                """
                INSERT INTO raw_github_events (event_id, event_type, actor_login, repo_name, created_at, raw_payload)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (event_id) DO NOTHING
            """,
                [
                    event_id,
                    event_type,
                    actor,
                    repo,
                    created_at,
                    raw_payload,
                ],
            )

    except Exception as e:
        print(f"Ingestion error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Live GitHub Event Producer...")
    print(f"Saving continuous events into local DuckDB lakehouse: '{DB_PATH}'")
    print("Press Ctrl+C to stop.\n")

    try:
        for batch_num in range(1, 6):  # Runs 5 loops for testing
            fetch_and_ingest_events()

            # Query current total count directly from DuckDB
            current_count = conn.execute(
                "SELECT COUNT(*) FROM raw_github_events"
            ).fetchone()[0]
            print(
                f"[Batch {batch_num}] Ingestion loop complete. Total unique events in DB: {current_count}"
            )
            time.sleep(5)  # Poll GitHub every 5 seconds
    except KeyboardInterrupt:
        print("\nStopping producer.")

    result = conn.execute("SELECT COUNT(*) FROM raw_github_events").fetchone()
    print(f"\n✅ Total records stored in 'raw_github_events': {result[0]}")
    conn.close()
import os
import sqlite3

for p in ['certinexus.db', 'backend/certinexus.db']:
    if os.path.exists(p):
        print(f"--- Database: {p} ---")
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"  Table {t}: {cnt} rows")
        conn.close()

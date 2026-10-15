import sqlite3
import os

for db_path in ['certinexus.db', 'backend/certinexus.db']:
    if os.path.exists(db_path):
        print(f"=== DB: {db_path} ===")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, title, file_path, file_type, file_size FROM certificates")
            rows = cur.fetchall()
            for r in rows:
                exists = os.path.exists(r[2]) if r[2] else False
                print(f"ID: {r[0]} | Title: {r[1]} | Type: {r[3]} | Path: {r[2]} (Exists: {exists})")
        except Exception as e:
            print(f"Error querying {db_path}: {e}")

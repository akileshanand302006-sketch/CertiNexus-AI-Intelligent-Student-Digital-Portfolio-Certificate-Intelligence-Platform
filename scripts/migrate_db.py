import sqlite3
import os

db_paths = ['certinexus.db', 'backend/certinexus.db']
for p in db_paths:
    if os.path.exists(p):
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute('PRAGMA table_info(certificates)')
        cols = [c[1] for c in cur.fetchall()]
        print(f'{p} cols count: {len(cols)}')
        if 'document_type' not in cols:
            cur.execute("ALTER TABLE certificates ADD COLUMN document_type VARCHAR(50) DEFAULT 'certificate'")
            conn.commit()
            print(f'Added document_type column to {p}')
        else:
            print(f'document_type already exists in {p}')
        conn.close()

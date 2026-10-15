import sys
import sqlite3
sys.path.insert(0, 'backend')

from app.api.auth import hash_password, verify_password
from app.core.database import db_manager

pwd = "Akilesh@30"
new_hash = hash_password(pwd)
print("New password hash generated.")

# 1. Update in MongoDB Atlas
if db_manager.connect():
    db = db_manager.db
    res = db.users.update_many(
        {"email": "akileshanand302006@gmail.com"},
        {"$set": {"password_hash": new_hash, "hashed_password": new_hash}}
    )
    print(f"MongoDB Atlas updated: {res.modified_count} user(s)")

# 2. Update in SQLite databases
for p in ["certinexus.db", "backend/certinexus.db"]:
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (new_hash, "akileshanand302006@gmail.com"))
        conn.commit()
        print(f"{p} updated: {cur.rowcount} row(s)")
        conn.close()
    except Exception as e:
        print(f"{p} notice: {e}")

print("Password setup completed successfully!")

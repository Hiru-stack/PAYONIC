import sqlite3
import os

db_path = 'payonic.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- TABLES ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    print("\n--- SAMPLE USER DATA ---")
    cursor.execute('SELECT id, username, email, role FROM "user" LIMIT 5;')
    users = cursor.fetchall()
    for user in users:
        print(user)
    
    conn.close()

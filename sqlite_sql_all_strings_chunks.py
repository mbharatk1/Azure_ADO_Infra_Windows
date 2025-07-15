import sqlite3
import pyodbc
import pandas as pd
import os

# SQL Server configuration
sql_server = 'YOUR_SQL_SERVER'       # e.g., 'localhost\\SQLEXPRESS'
sql_database = 'YOUR_DATABASE'
sql_username = 'YOUR_USERNAME'
sql_password = 'YOUR_PASSWORD'

# Connect to SQL Server
conn_sql = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={sql_server};DATABASE={sql_database};UID={sql_username};PWD={sql_password}'
)
cursor_sql = conn_sql.cursor()

# List of SQLite database file paths
sqlite_databases = [
    r"C:\Path\To\YourDB1.db",
    r"C:\Path\To\YourDB2.db"
]

# Chunk size for insert to avoid MemoryError
chunk_size = 1000

# Process each SQLite database
for db_file in sqlite_databases:
    db_name = os.path.basename(db_file).split('.')[0]

    print(f"\n📦 Processing SQLite DB: {db_name}")

    # Connect to SQLite
    conn_sqlite = sqlite3.connect(db_file)
    cursor_sqlite = conn_sqlite.cursor()

    # Get list of tables
    cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor_sqlite.fetchall()]

    for table_name in tables:
        new_table_name = f"{db_name}_{table_name}"
        print(f"🔄 Migrating table: {table_name} → SQL: {new_table_name}")

        # Read table into DataFrame
        try:
            df_sqlite = pd.read_sql_query(f"SELECT * FROM {table_name}", conn_sqlite)
            df_sqlite = df_sqlite.astype(str)  # Force string type
        except Exception as e:
            print(f"❌ Failed to read table {table_name}: {e}")
            continue

        if not df_sqlite.empty:
            # Create SQL Server table if not exists
            try:
                column_definitions = ', '.join([f"[{col}] NVARCHAR(MAX)" for col in df_sqlite.columns])
                cursor_sql.execute(f"""
                    IF NOT EXISTS (
                        SELECT * FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_NAME = '{new_table_name}'
                    )
                    BEGIN
                        CREATE TABLE [{new_table_name}] ({column_definitions})
                    END
                """)
                conn_sql.commit()
            except Exception as e:
                print(f"❌ Error creating table {new_table_name}: {e}")
                continue

            # Prepare insert statement
            placeholders = ', '.join(['?' for _ in df_sqlite.columns])
            columns_formatted = ', '.join([f"[{col}]" for col in df_sqlite.columns])
            insert_query = f"INSERT INTO [{new_table_name}] ({columns_formatted}) VALUES ({placeholders})"

            # Insert in chunks
            try:
                rows = df_sqlite.values.tolist()
                cursor_sql.fast_executemany = True

                for i in range(0, len(rows), chunk_size):
                    chunk = rows[i:i + chunk_size]
                    cursor_sql.executemany(insert_query, chunk)
                    conn_sql.commit()
                    print(f"✅ Inserted rows {i}–{i + len(chunk)} into {new_table_name}")

                print(f"🎯 Table {new_table_name} migrated successfully!")
            except Exception as e:
                print(f"❌ Error inserting data into {new_table_name}: {e}")
                continue
        else:
            print(f"⚠️ Table {table_name} is empty—skipped.")

    conn_sqlite.close()

# Final cleanup
conn_sql.close()
print("\n✅✅ All tables migrated successfully!")

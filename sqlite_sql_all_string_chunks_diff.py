import sqlite3
import pyodbc
import pandas as pd
import os

# 🔐 SQL Server configuration
sql_server = 'YOUR_SQL_SERVER'
sql_database = 'YOUR_DATABASE'
sql_username = 'YOUR_USERNAME'
sql_password = 'YOUR_PASSWORD'

# 📦 List of SQLite database paths
sqlite_databases = [
    r"C:\Path\To\YourDB1.db",
    r"C:\Path\To\YourDB2.db"
]

# ⚙️ Connect to SQL Server
conn_sql = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={sql_server};DATABASE={sql_database};UID={sql_username};PWD={sql_password}'
)
cursor_sql = conn_sql.cursor()

# 🚚 Process each SQLite DB
for db_file in sqlite_databases:
    db_name = os.path.basename(db_file).split('.')[0]
    print(f"\n📦 Processing: {db_file}")

    conn_sqlite = sqlite3.connect(db_file)
    cursor_sqlite = conn_sqlite.cursor()

    # 🔍 Fetch table names
    cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor_sqlite.fetchall()]

    for table_name in tables:
        new_table_name = f"{db_name}_{table_name}"
        print(f"🔄 Migrating table: {table_name} → {new_table_name}")

        try:
            df_sqlite = pd.read_sql_query(f"SELECT * FROM {table_name}", conn_sqlite)
            df_sqlite = df_sqlite.astype(str)
        except Exception as e:
            print(f"❌ Failed to read table {table_name}: {e}")
            continue

        if not df_sqlite.empty:
            try:
                column_defs = ', '.join([f"[{col}] NVARCHAR(MAX)" for col in df_sqlite.columns])
                cursor_sql.execute(f"""
                    IF NOT EXISTS (
                        SELECT * FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_NAME = '{new_table_name}'
                    )
                    BEGIN
                        CREATE TABLE [{new_table_name}] ({column_defs})
                    END
                """)
                conn_sql.commit()
            except Exception as e:
                print(f"❌ Error creating table {new_table_name}: {e}")
                continue

            # ✅ Prepare insert query
            placeholders = ', '.join(['?' for _ in df_sqlite.columns])
            column_list = ', '.join([f"[{col}]" for col in df_sqlite.columns])
            insert_query = f"INSERT INTO [{new_table_name}] ({column_list}) VALUES ({placeholders})"

            # 🚀 Use memory-efficient row iterator
            try:
                cursor_sql.fast_executemany = True
                rows = df_sqlite.itertuples(index=False, name=None)
                cursor_sql.executemany(insert_query, rows)
                conn_sql.commit()
                print(f"✅ Inserted {len(df_sqlite)} rows into {new_table_name}")
            except Exception as e:
                print(f"❌ Error inserting into {new_table_name}: {e}")
                continue
        else:
            print(f"⚠️ Table {table_name} is empty—skipped.")

    conn_sqlite.close()

# 🧹 Finalize
conn_sql.close()
print("\n🎉 All tables migrated successfully!")

import sqlite3
import pyodbc
import pandas as pd
import os

# 🛡️ SQL Server connection details
sql_server = 'YOUR_SQL_SERVER'       # e.g., 'localhost\\SQLEXPRESS'
sql_database = 'YOUR_DATABASE'
sql_username = 'YOUR_USERNAME'
sql_password = 'YOUR_PASSWORD'

# 🔗 Connect to SQL Server
conn_sql = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={sql_server};DATABASE={sql_database};UID={sql_username};PWD={sql_password}'
)
cursor_sql = conn_sql.cursor()

# 📋 List of SQLite databases to process
sqlite_databases = [
    r"C:\Path\To\RSRMatter.db"  # Add more paths as needed
]

# 🚚 Migrate each SQLite DB
for db_file in sqlite_databases:
    db_name = os.path.basename(db_file).split('.')[0]  # Extract base name

    # 🔌 Connect to SQLite
    conn_sqlite = sqlite3.connect(db_file)
    cursor_sqlite = conn_sqlite.cursor()

    # 🧠 Fetch table names
    cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor_sqlite.fetchall()]

    for table_name in tables:
        new_table_name = f"{db_name}_{table_name}"

        # 📥 Load SQLite table into DataFrame
        df_sqlite = pd.read_sql_query(f"SELECT * FROM {table_name}", conn_sqlite)

        # 🔄 Force all data to string to avoid insert type issues
        df_sqlite = df_sqlite.astype(str)

        if not df_sqlite.empty:
            try:
                # 🔨 Create table if it doesn't exist
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

            try:
                # 🚀 Bulk insert data
                placeholders = ', '.join(['?' for _ in df_sqlite.columns])
                columns_formatted = ', '.join([f"[{col}]" for col in df_sqlite.columns])
                insert_query = f"INSERT INTO [{new_table_name}] ({columns_formatted}) VALUES ({placeholders})"
                
                cursor_sql.fast_executemany = True
                cursor_sql.executemany(insert_query, df_sqlite.values.tolist())
                conn_sql.commit()

                print(f"✅ {new_table_name} migrated successfully!")
            except Exception as e:
                print(f"❌ Error inserting data into {new_table_name}: {e}")
                continue

    conn_sqlite.close()

# 🧹 Cleanup
conn_sql.close()
print("🎉 All tables migrated successfully!")

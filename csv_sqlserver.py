import pandas as pd
import pyodbc

# Step 1: Load pipe-delimited CSV
csv_path = 'data.csv'  # Update this to your actual file path
df = pd.read_csv(csv_path, sep='|')

# Step 2: Set up the SQL Server connection
server = 'your_server_name'  # e.g., 'localhost\\SQLEXPRESS'
database = 'your_database'
username = 'your_username'
password = 'your_password'

conn_str = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={server};
    DATABASE={database};
    UID={username};
    PWD={password};
"""
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Step 3: Insert data into SQL Server table
table_name = 'your_table_name'

# Insert each row
for _, row in df.iterrows():
    placeholders = ', '.join(['?'] * len(row))
    sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
    cursor.execute(sql, tuple(row))

conn.commit()
cursor.close()
conn.close()

print("✅ Data loaded from pipe-delimited CSV successfully!")

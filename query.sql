import pyodbc

# Connect to SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server;DATABASE=your_db;UID=your_user;PWD=your_password'
)
cursor = conn.cursor()

# Query to list objects
query = """
SELECT name, type_desc
FROM sys.objects
WHERE type IN ('U', 'V', 'P', 'FN', 'IF', 'TF')  -- Tables, Views, Procedures, Functions
"""

cursor.execute(query)
rows = cursor.fetchall()

# Display results
for row in rows:
    print(f"{row.name} ({row.type_desc})")

cursor.close()
conn.close()

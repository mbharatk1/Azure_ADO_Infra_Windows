JSON  -- params.json 

{
    "queries": [
        {
            "filename": "C:/Reports/employees.csv",
            "query": "SELECT id, name, salary FROM Employees WHERE salary > 50000"
        },
        {
            "filename": "C:/Reports/departments.csv",
            "query": "SELECT dept_id, dept_name FROM Departments"
        },
        {
            "filename": "C:/Reports/projects.csv",
            "query": "SELECT project_id, project_name, budget FROM Projects"
        }
    ]
}



python script 

import pyodbc
import pandas as pd
import json
import logging

# Configure logging
logging.basicConfig(filename="sql_export.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Define SQL Server connection details
server = "YourSQLServer"  # Replace with actual server name
database = "YourDatabase"  # Replace with actual database name
username = "YourUsername"  # Replace with actual SQL login
password = "YourPassword"  # Replace with actual password

# Load JSON parameters file
try:
    with open("params.json", "r") as file:
        params = json.load(file)
except Exception as e:
    logging.error(f"Error loading JSON file: {e}")
    print("❌ Error loading JSON file. Check 'sql_export.log' for details.")
    exit()

# Establish connection to SQL Server
try:
    conn = pyodbc.connect(f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}")
except Exception as e:
    logging.error(f"SQL Server connection failed: {e}")
    print("❌ Database connection error. Check 'sql_export.log' for details.")
    exit()

# Execute queries and save output
for item in params["queries"]:
    filename = item["filename"]
    query = item["query"]

    try:
        df = pd.read_sql(query, conn)
        df.to_csv(filename, index=False)
        logging.info(f"✅ Query executed successfully. Output saved to {filename}")
        print(f"✅ Query result saved to {filename}")
    except Exception as e:
        logging.error(f"Query execution failed for {filename}: {e}")
        print(f"❌ Error executing query for {filename}. Check 'sql_export.log' for details.")

# Close connection
conn.close()
logging.info("✅ SQL Server connection closed.")
print("✅ Process completed. Check 'sql_export.log' for details.")




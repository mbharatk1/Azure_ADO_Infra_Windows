import sqlite3

for item in queries:
    db = item["db"]
    query = item["query"]
    filename = item["filename"]

    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        with open(filename, "w", encoding="utf-8") as f:
            f.write('\t'.join(columns) + '\n')
            for row in rows:
                f.write('\t'.join(str(cell) for cell in row) + '\n')

        print(f"✅ Query from {db} saved to {filename}")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error with {db}: {e}")

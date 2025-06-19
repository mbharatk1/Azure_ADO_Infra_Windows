import requests
import csv
import time

# === Configuration ===
access_token = "your_access_token"              # Replace with your valid access token
customer_id = "100"                              # Replace with your customer ID
library_id = "ACTIVE_US"                         # Replace with your library ID
work_server = "your-imanage-instance.com"        # Replace with your iManage server host
csv_file = "workspaces.csv"                      # Workspace input file

# === API Endpoints ===
base_url = f"https://{work_server}/work/api/v2/customers/{customer_id}/libraries/{library_id}"
create_url = f"{base_url}/workspaces"
list_url = f"{base_url}/workspaces"

# === Headers ===
headers = {
    "X-Auth-Token": access_token,
    "Content-Type": "application/json"
}

# === Step 1: Fetch existing workspace names ===
print("🔍 Fetching existing workspaces...")
try:
    response = requests.get(list_url, headers=headers)
    response.raise_for_status()
    existing_workspaces = response.json().get("data", [])
    existing_names = set(ws["name"].strip().lower() for ws in existing_workspaces)
    print(f"📌 Found {len(existing_names)} existing workspaces.")
except Exception as e:
    print(f"❌ Failed to fetch existing workspaces: {e}")
    exit(1)

# === Step 2: Read CSV and create only new workspaces ===
print("📥 Reading workspace definitions from CSV...")
with open(csv_file, mode="r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        ws_name = row["name"].strip()

        if ws_name.lower() in existing_names:
            print(f"⏭️  Skipping existing workspace: {ws_name}")
            continue

        payload = {
            "name": ws_name,
            "description": row["description"],
            "default_security": "private",  # or 'view' / 'public'
            "custom1": row["custom1"],
            "custom2": row["custom2"],
            "author": row["author"],
            "owner": row["owner"]
        }

        try:
            create_resp = requests.post(create_url, headers=headers, json=payload)
            create_resp.raise_for_status()
            new_id = create_resp.json().get("data", {}).get("id", "N/A")
            print(f"✅ Created: {ws_name} → ID: {new_id}")
        except Exception as e:
            print(f"❌ Error creating {ws_name}: {e}")

        time.sleep(0.5)  # Optional: pause to avoid API throttling


workspaces.csv
----------------
name,description,custom1,custom2,author,owner
Project Nova,Confidential Nova workspace,ClientX,Matter123,jdoe,jdoe
Project Vega,Workspace for Vega client,ClientY,Matter456,jdoe,jdoe


import csv
import requests

# === Configuration ===
host = "your-imanage-host.com"
customer_id = "100"
library_id = "active_us"
access_token = "your_access_token"
csv_file = "workspace_updates.csv"

headers = {
    "X-Auth-Token": access_token,
    "Content-Type": "application/json"
}

# === Loop through each row in the CSV and PATCH ===
with open(csv_file, "r", newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        workspace_id = row["workspace_id"]
        description = row["description"]

        url = f"https://{host}/work/api/v2/customers/{customer_id}/libraries/{library_id}/workspaces/{workspace_id}"
        payload = {"description": description}

        try:
            response = requests.patch(url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"✅ Updated {workspace_id}: {description}")
        except requests.exceptions.RequestException as err:
            print(f"❌ Failed to update {workspace_id}: {err}")



workspace_id,description
active_us!7601,"Updated Description 1"
active_us!7745,"Updated Description 2"
active_us!9230,"Another update for this one"

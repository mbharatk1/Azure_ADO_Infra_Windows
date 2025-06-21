import csv
import requests

# === Config ===
host = "your-imanage-host.com"
customer_id = "100"
library_id = "active_us"
access_token = "your_token"
csv_input = "workspace_updates.csv"
success_log = "success_updates.csv"
failure_log = "failed_updates.csv"

headers = {
    "X-Auth-Token": access_token,
    "Content-Type": "application/json"
}

successes = []
failures = []

with open(csv_input, "r", newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)

    for row in reader:
        workspace_id = row["workspace_id"]
        description = row["description"]

        url = f"https://{host}/work/api/v2/customers/{customer_id}/libraries/{library_id}/workspaces/{workspace_id}"
        payload = {"description": description}

        try:
            response = requests.patch(url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"✅ Updated: {workspace_id}")
            successes.append(row)
        except requests.exceptions.RequestException as err:
            print(f"❌ Failed: {workspace_id} — {err}")
            row["error"] = str(err)
            failures.append(row)

# Write success file
if successes:
    with open(success_log, "w", newline='', encoding='utf-8') as out_success:
        fieldnames = list(successes[0].keys())
        writer = csv.DictWriter(out_success, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(successes)

# Write failure file
if failures:
    with open(failure_log, "w", newline='', encoding='utf-8') as out_fail:
        fieldnames = list(failures[0].keys())
        writer = csv.DictWriter(out_fail, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(failures)

print(f"\n📦 Successes saved: {len(successes)}")
print(f"🚨 Failures logged: {len(failures)}")

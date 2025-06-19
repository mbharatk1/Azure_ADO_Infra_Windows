import requests
import json
import sys

# Define authentication and workspace details
x_auth_token = "your_x_auth_token"
customer_id = "your_customer_id"
server_name = "your_server_name"
library_id = "your_library_id"
workspace_id = "your_workspace_id"

headers = {
    "X-Auth-Token": x_auth_token,
    "Content-Type": "application/json"
}

# Step 1️⃣: Retrieve workspace profile
workspace_profile_url = f"https://{server_name}/work/api/v2/customers/{customer_id}/libraries/{library_id}/workspaces/{workspace_id}"
print(f"🔍 Fetching workspace details for {workspace_id}...")

try:
    response = requests.get(workspace_profile_url, headers=headers)
    response.raise_for_status()
    workspace_details = response.json()
    print("✅ Workspace details retrieved successfully!")
    print("📌 Available attributes:", json.dumps(workspace_details.get("data"), indent=2))
except requests.exceptions.RequestException as e:
    print("🔥 Error retrieving workspace details!")
    print("⚠️ Error Message:", e)
    sys.exit()

# Step 2️⃣: Check permissions
permissions_url = f"https://{server_name}/work/api/v2/customers/{customer_id}/libraries/{library_id}/workspaces/{workspace_id}/operations"
print("🔑 Checking workspace modification permissions...")

try:
    response = requests.get(permissions_url, headers=headers)
    response.raise_for_status()
    permissions = response.json()
    if not permissions.get("data", {}).get("modify", False):
        print("❌ Modification not allowed. You lack permissions to update attributes.")
        sys.exit()
    print("✅ You have permission to modify workspace attributes!")
except requests.exceptions.RequestException as e:
    print("🔥 Error retrieving modification permissions!")
    print("⚠️ Error Message:", e)
    sys.exit()

# Step 3️⃣: Attempt to update the 'author' field
payload = {
    "profile": {
        "author": "New_Author_Name"
    }
}
update_url = workspace_profile_url  # same as profile URL
print("🔄 Attempting to update the author field...")

try:
    response = requests.patch(update_url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    updated_details = response.json()
    print("✅ Author updated successfully!")
    print("🔄 Updated workspace details:", json.dumps(updated_details, indent=2))
except requests.exceptions.RequestException as e:
    print("🔥 Error updating author field!")
    print("⚠️ Error Message:", e)

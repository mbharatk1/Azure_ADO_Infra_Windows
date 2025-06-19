import requests
import json

# === Configuration ===
access_token = "your_access_token"
customer_id = "100"                 # Replace with your actual customer ID
library_id = "ACTIVE_US"           # Replace with your actual library ID
work_server = "your-server.com"    # e.g., imanage.example.com

# === Step 1: Define the workspace to be created ===
workspace_payload = {
    "name": "Project Phoenix",
    "description": "Workspace for Phoenix legal project",
    "default_security": "private",     # Options: private, view, public
    "custom1": "Client_XYZ",           # Optional client/matter metadata
    "custom2": "Matter_ABC",
    "author": "b.madamanchi",
    "owner": "b.madamanchi"
}

workspace_url = f"https://{work_server}/work/api/v2/customers/{customer_id}/libraries/{library_id}/workspaces"
headers = {
    "X-Auth-Token": access_token,
    "Content-Type": "application/json"
}

# === Step 2: Create the workspace ===
try:
    print("🚀 Creating workspace...")
    create_resp = requests.post(workspace_url, headers=headers, json=workspace_payload)
    create_resp.raise_for_status()
    workspace = create_resp.json()
    workspace_id = workspace.get("data", {}).get("id")
    print(f"✅ Workspace created with ID: {workspace_id}")
except Exception as e:
    print(f"❌ Error creating workspace: {e}")
    exit(1)

# === Step 3: Assign permissions ===
permissions_payload = {
    "entries": [
        {"type": "user", "id": "b.madamanchi", "access_type": "full_access"},
        {"type": "group", "id": "FinanceTeam", "access_type": "read_write"}
    ]
}

permissions_url = f"https://{work_server}/work/api/v2/customers/{customer_id}/libraries/{library_id}/workspaces/{workspace_id}/users-and-groups"

try:
    print("🔐 Applying permissions...")
    perm_resp = requests.patch(permissions_url, headers=headers, json=permissions_payload)
    perm_resp.raise_for_status()
    print("✅ Permissions successfully assigned!")
except Exception as e:
    print(f"❌ Error assigning permissions: {e}")
    exit(1)

import requests
import datetime
import os
import sys
from collections import defaultdict

# Read parameters from file
param_file = r"C:\Config\params.txt"
params = {}
with open(param_file, 'r') as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            params[key.strip()] = value.strip()

username = params.get("username")
password = params.get("password")
client_id = params.get("client_id")
client_secret = params.get("client_secret")
work_server = params.get("work_server")

# Log file
log_file = r"C:\Logs\iManage_API_Log.txt"

def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as log:
        log.write(f"{timestamp} - {message}\n")

write_log("Starting iManage workspace retrieval...")

# Step 1: Authenticate
oauth_url = f"https://{work_server}/auth/oauth2/token"
auth_data = {
    "username": username,
    "password": password,
    "grant_type": "password",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "admin"
}

try:
    write_log("Requesting OAuth Token...")
    token_response = requests.post(oauth_url, data=auth_data)
    token_response.raise_for_status()
    access_token = token_response.json().get("access_token")
    write_log("OAuth Token retrieved successfully.")
except requests.exceptions.RequestException as e:
    write_log(f"ERROR: Failed to retrieve OAuth Token - {e}")
    sys.exit(1)

# Step 2: Retrieve workspaces
workspace_url = f"https://{work_server}/work/api/v2/customers/1/libraries/CH/workspaces"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

try:
    write_log("Fetching workspace details...")
    response = requests.get(workspace_url, headers=headers)
    response.raise_for_status()
    workspace_list = response.json()
    write_log("Workspace details retrieved successfully.")
except requests.exceptions.RequestException as e:
    write_log(f"ERROR: Failed to retrieve workspace details - {e}")
    sys.exit(1)

# Step 3: Organize by Matter Class
workspace_hierarchy = defaultdict(list)

for workspace in workspace_list:
    matter_class = workspace.get("custom2", "Unknown")
    workspace_hierarchy[matter_class].append({
        "Workspace Name": workspace.get("name"),
        "Workspace ID": workspace.get("id"),
        "Custom Attributes": workspace
    })

# Step 4: Display output
for matter_class, workspaces in workspace_hierarchy.items():
    print(f"Matter Class: {matter_class}")
    for ws in workspaces:
        print(f"  Workspace: {ws['Workspace Name']}")
        print(f"    ID: {ws['Workspace ID']}")
        print(f"    Custom Attributes:")
        for key, value in ws['Custom Attributes'].items():
            print(f"      {key}: {value}")

write_log("Workspace retrieval completed successfully.")

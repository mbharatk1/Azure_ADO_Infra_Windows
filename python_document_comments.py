import requests
import datetime
import sys

# === Step 1: Load parameters from file ===
param_file_path = r"C:\Config\params.txt"
params = {}

try:
    with open(param_file_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                params[key.strip()] = value.strip()
except FileNotFoundError:
    print(f"❌ ERROR: Parameter file not found at {param_file_path}")
    sys.exit(1)

username = params.get("username")
password = params.get("password")
client_id = params.get("client_id")
client_secret = params.get("client_secret")
work_server = params.get("work_server")

customer_id = "1"        # Update if needed
library_id = "CH"        # Update if needed
document_id = "12345"    # Replace with actual document ID

log_file = r"C:\Logs\iManage_API_Log.txt"

def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as log:
        log.write(f"{timestamp} - {message}\n")

write_log("🚀 Starting document comments update script...")

# === Step 2: Authenticate ===
auth_url = f"https://{work_server}/auth/oauth2/token"
auth_payload = {
    "username": username,
    "password": password,
    "grant_type": "password",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "admin"
}

try:
    write_log("🔐 Requesting OAuth token...")
    auth_response = requests.post(auth_url, data=auth_payload)
    auth_response.raise_for_status()
    access_token = auth_response.json().get("access_token")
    if not access_token:
        raise ValueError("Access token not found in response.")
    write_log("✅ Token successfully retrieved.")
except Exception as e:
    write_log(f"❌ ERROR: Failed to authenticate - {e}")
    sys.exit(1)

# === Step 3: Check if document exists ===
doc_url = f"https://{work_server}/work/api/v2/customers/{customer_id}/libraries/{library_id}/documents/{document_id}"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

try:
    write_log("📄 Verifying document existence...")
    check_response = requests.get(doc_url, headers=headers)
    check_response.raise_for_status()
    write_log(f"📌 Document found: {document_id}")
except Exception as e:
    write_log(f"❌ ERROR: Document not found - {e}")
    print(f"ERROR: Document {document_id} does not exist.")
    sys.exit(1)

# === Step 4: Patch the document comments ===
update_payload = {
    "comments": "Updated comments for the document."
}
headers["Content-Type"] = "application/json"

try:
    write_log("✏️ Updating document comments...")
    patch_response = requests.patch(doc_url, headers=headers, json=update_payload)
    patch_response.raise_for_status()
    write_log("✅ Document comments updated successfully.")
    print("✅ Document comments updated successfully.")
except Exception as e:
    write_log(f"❌ ERROR: Failed to update comments - {e}")
    print(f"ERROR: Unable to update comments for document ID {document_id}.")
    sys.exit(1)

write_log("🏁 Script execution completed.")

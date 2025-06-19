import requests
import datetime
import sys

# === Step 1: Load credentials from parameter file ===
param_file_path = r"C:\Config\params.txt"
params = {}

try:
    with open(param_file_path, "r") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                params[key.strip()] = value.strip()
except FileNotFoundError:
    print(f"❌ Parameter file not found at {param_file_path}")
    sys.exit(1)

# Extract values
username = params.get("username")
password = params.get("password")
client_id = params.get("client_id")
client_secret = params.get("client_secret")
work_server = params.get("work_server")

# === Step 2: Logging setup ===
log_file_path = r"C:\Logs\iManage_API_Log.txt"

def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a") as log:
        log.write(f"{timestamp} - {message}\n")

write_log("🔧 Starting iManage connection test...")

# === Step 3: Authenticate with iManage Work ===
auth_url = f"https://{work_server}/auth/oauth2/token"
payload = {
    "username": username,
    "password": password,
    "grant_type": "password",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "admin"
}

try:
    write_log("🔐 Requesting OAuth Token...")
    response = requests.post(auth_url, data=payload)
    response.raise_for_status()

    token_data = response.json()
    access_token = token_data.get("access_token")

    if access_token:
        write_log("✅ Successfully connected to iManage Work!")
        print("✅ Successfully connected to iManage Work!")
    else:
        write_log("❌ ERROR: Authentication failed. No token received.")
        print("❌ Authentication failed. Check credentials.")
        sys.exit(1)
except requests.exceptions.RequestException as e:
    write_log(f"🔥 ERROR: Unable to connect to iManage Work - {e}")
    print(f"🔥 ERROR: Unable to connect to iManage Work - {e}")
    sys.exit(1)

write_log("✅ iManage connection test completed successfully.")

import requests
import csv

def authenticate(server_url, username, password):
    url = f"{server_url}/work/api/v2/auth/login"
    response = requests.post(url, json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()['access_token']
    raise Exception("Authentication failed")

def get_folders(server_url, headers, library_id, workspace_id, folder_id=None):
    if folder_id:
        url = f"{server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders/{folder_id}/folders"
    else:
        url = f"{server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders"
    response = requests.get(url, headers=headers)
    return response.json().get('data', []) if response.status_code == 200 else []

def get_documents(server_url, headers, library_id, workspace_id, folder_id=None):
    if folder_id:
        url = f"{server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders/{folder_id}/documents"
    else:
        url = f"{server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/documents"
    response = requests.get(url, headers=headers)
    return response.json().get('data', []) if response.status_code == 200 else []

def export_folder_stats(server_url, username, password, library_id, workspace_id, filename='folder_stats.csv'):
    token = authenticate(server_url, username, password)
    headers = {"Authorization": f"Bearer {token}"}

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Folder Name', 'Folder ID', 'Parent ID', 'Document Count', 'Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        _export_recursive(writer, server_url, headers, library_id, workspace_id)

    print(f"Exported to {filename}")

def _export_recursive(writer, server_url, headers, library_id, workspace_id, folder_id=None, path=""):
    folders = get_folders(server_url, headers, library_id, workspace_id, folder_id)
    for folder in folders:
        folder_path = f"{path}/{folder['name']}"
        folder_id_val = folder['id']
        documents = get_documents(server_url, headers, library_id, workspace_id, folder_id_val)
        writer.writerow({
            'Folder Name': folder['name'],
            'Folder ID': folder_id_val,
            'Parent ID': folder_id or workspace_id,
            'Document Count': len(documents),
            'Path': folder_path
        })
        _export_recursive(writer, server_url, headers, library_id, workspace_id, folder_id_val, folder_path)

# Example usage:
export_folder_stats(
    server_url="https://your-imanage-server",
    username="your_username",
    password="your_password",
    library_id="your_library_id",
    workspace_id="your_workspace_id",
    filename="workspace_folder_stats.csv"
)

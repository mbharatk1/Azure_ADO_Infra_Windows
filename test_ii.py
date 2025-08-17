def get_folders(server_url, headers, library_id, workspace_id, folder_id=None):
    if folder_id:
        url = f"{server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders/{folder_id}/folders"
    else:
        url = f"{server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders"
    response = requests.get(url, headers=headers)
    return response.json().get('data', []) if response.status_code == 200 else []

def extract_all_folders(server_url, headers, library_id, workspace_id, folder_id=None, path=""):
    folders = get_folders(server_url, headers, library_id, workspace_id, folder_id)
    for folder in folders:
        folder_path = f"{path}/{folder['name']}"
        print(f"Folder: {folder['name']} | ID: {folder['id']} | Path: {folder_path}")
        extract_all_folders(server_url, headers, library_id, workspace_id, folder['id'], folder_path)

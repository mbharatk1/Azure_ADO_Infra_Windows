import requests
import csv

class iManageFolderStatsExporter:
    def __init__(self, server_url, username, password):
        self.server_url = server_url
        self.token = self.authenticate(username, password)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def authenticate(self, username, password):
        url = f"{self.server_url}/work/api/v2/auth/login"
        response = requests.post(url, json={"username": username, "password": password})
        if response.status_code == 200:
            return response.json()['access_token']
        raise Exception("Authentication failed")

    def get_folders(self, library_id, workspace_id, folder_id=None):
        if folder_id:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders/{folder_id}/folders"
        else:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders"
        response = requests.get(url, headers=self.headers)
        return response.json().get('data', []) if response.status_code == 200 else []

    def get_documents(self, library_id, workspace_id, folder_id=None):
        if folder_id:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders/{folder_id}/documents"
        else:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/documents"
        response = requests.get(url, headers=self.headers)
        return response.json().get('data', []) if response.status_code == 200 else []

    def export_folder_stats(self, library_id, workspace_id, filename='folder_stats.csv'):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Folder Name', 'Folder ID', 'Parent ID', 'Document Count', 'Path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            self._export_recursive(writer, library_id, workspace_id)

        print(f"Folder stats exported to {filename}")

    def _export_recursive(self, writer, library_id, workspace_id, folder_id=None, path=""):
        folders = self.get_folders(library_id, workspace_id, folder_id)
        for folder in folders:
            folder_path = f"{path}/{folder['name']}"
            folder_id_val = folder['id']
            documents = self.get_documents(library_id, workspace_id, folder_id_val)
            writer.writerow({
                'Folder Name': folder['name'],
                'Folder ID': folder_id_val,
                'Parent ID': folder_id or workspace_id,
                'Document Count': len(documents),
                'Path': folder_path
            })
            self._export_recursive(writer, library_id, workspace_id, folder_id_val, folder_path)

# Usage
exporter = iManageFolderStatsExporter("https://your-imanage-server", "username", "password")
exporter.export_folder_stats("your_library_id", "your_workspace_id", "workspace_folder_stats.csv")

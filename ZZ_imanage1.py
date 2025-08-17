import requests
import json

class iManageHierarchyLister:
    def __init__(self, server_url, username, password):
        self.server_url = server_url
        self.token = self.authenticate(username, password)
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def authenticate(self, username, password):
        auth_url = f"{self.server_url}/work/api/v2/auth/login"
        auth_data = {"username": username, "password": password}
        
        response = requests.post(auth_url, json=auth_data)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception("Authentication failed")
    
    def get_workspaces(self, library_id):
        url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    
    def get_folders(self, library_id, workspace_id, folder_id=None):
        if folder_id:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders/{folder_id}/folders"
        else:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders"
            
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    
    def get_documents(self, library_id, workspace_id, folder_id=None):
        if folder_id:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/folders/{folder_id}/documents"
        else:
            url = f"{self.server_url}/work/api/v2/libraries/{library_id}/workspaces/{workspace_id}/documents"
            
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    
    def list_hierarchy(self, library_id, workspace_id=None, folder_id=None, level=0):
        indent = "  " * level
        
        if workspace_id is None:
            # List workspaces
            workspaces = self.get_workspaces(library_id)
            for workspace in workspaces:
                print(f"{indent}[WORKSPACE] {workspace['name']} (ID: {workspace['id']})")
                self.list_hierarchy(library_id, workspace['id'], level=level+1)
        else:
            # List folders
            folders = self.get_folders(library_id, workspace_id, folder_id)
            for folder in folders:
                print(f"{indent}[FOLDER] {folder['name']} (ID: {folder['id']})")
                self.list_hierarchy(library_id, workspace_id, folder['id'], level=level+1)
            
            # List documents
            documents = self.get_documents(library_id, workspace_id, folder_id)
            for document in documents:
                print(f"{indent}[DOCUMENT] {document['name']} (ID: {document['id']}, Version: {document.get('version', 'N/A')})")
    
    def export_to_csv(self, library_id, filename='imanage_hierarchy.csv'):
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Type', 'Name', 'ID', 'Parent_ID', 'Workspace_ID', 'Path', 'Version', 'Extension', 'Size']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            self._export_hierarchy_csv(writer, library_id)
        
        print(f"Hierarchy exported to {filename}")
    
    def _export_hierarchy_csv(self, writer, library_id, workspace_id=None, folder_id=None, path=""):
        if workspace_id is None:
            workspaces = self.get_workspaces(library_id)
            for workspace in workspaces:
                workspace_path = f"/{workspace['name']}"
                writer.writerow({
                    'Type': 'WORKSPACE',
                    'Name': workspace['name'],
                    'ID': workspace['id'],
                    'Parent_ID': '',
                    'Workspace_ID': workspace['id'],
                    'Path': workspace_path,
                    'Version': '',
                    'Extension': '',
                    'Size': ''
                })
                self._export_hierarchy_csv(writer, library_id, workspace['id'], path=workspace_path)
        else:
            # Export folders
            folders = self.get_folders(library_id, workspace_id, folder_id)
            for folder in folders:
                folder_path = f"{path}/{folder['name']}"
                writer.writerow({
                    'Type': 'FOLDER',
                    'Name': folder['name'],
                    'ID': folder['id'],
                    'Parent_ID': folder_id or workspace_id,
                    'Workspace_ID': workspace_id,
                    'Path': folder_path,
                    'Version': '',
                    'Extension': '',
                    'Size': ''
                })
                self._export_hierarchy_csv(writer, library_id, workspace_id, folder['id'], folder_path)
            
            # Export documents
            documents = self.get_documents(library_id, workspace_id, folder_id)
            for document in documents:
                writer.writerow({
                    'Type': 'DOCUMENT',
                    'Name': document['name'],
                    'ID': document['id'],
                    'Parent_ID': folder_id or workspace_id,
                    'Workspace_ID': workspace_id,
                    'Path': f"{path}/{document['name']}",
                    'Version': document.get('version', ''),
                    'Extension': document.get('extension', ''),
                    'Size': document.get('size', '')
                })

# Usage
lister = iManageHierarchyLister("https://your-imanage-server", "username", "password")

# Print hierarchy to console
lister.list_hierarchy("your_library_id")

# Export to CSV
lister.export_to_csv("your_library_id", "my_imanage_structure.csv")

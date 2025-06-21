# get_workspaces.py

import requests
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_fields = ['server', 'username', 'password', 'client_id', 'client_secret', 'customer_id']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required config fields: {missing_fields}")
        
        return config
    except FileNotFoundError:
        print(f"ERROR: Config file '{config_file}' not found!")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in '{config_file}'")
        return None

def get_access_token(config):
    """Get OAuth2 access token from iManage"""
    
    print("Getting OAuth2 access token...")
    print(f"Server: {config['server']}")
    print(f"Username: {config['username']}")
    
    token_url = f"{config['server'].rstrip('/')}/auth/oauth2/token"
    token_data = {
        'grant_type': 'password',
        'username': config['username'],
        'password': config['password'],
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'scope': config.get('scope', 'openid profile email')
    }
    
    try:
        response = requests.post(
            token_url,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30,
            verify=config.get('verify_ssl', False)
        )
        
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            
            if access_token:
                print("SUCCESS: Access token received!")
                return {
                    'access_token': access_token,
                    'token_type': token_response.get('token_type', 'Bearer'),
                    'expires_in': token_response.get('expires_in'),
                    'received_at': datetime.now().isoformat()
                }
            
        print(f"ERROR: Authentication failed - {response.status_code}")
        print(f"Response: {response.text}")
        return None
        
    except Exception as e:
        print(f"ERROR: Authentication failed - {e}")
        return None

def get_customer_libraries(config, token_info):
    """Get libraries for customer"""
    
    libraries_url = f"{config['server'].rstrip('/')}/work/api/v2/customers/{config['customer_id']}/libraries"
    headers = {
        'Authorization': f"{token_info['token_type']} {token_info['access_token']}",
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            libraries_url, 
            headers=headers, 
            timeout=30,
            verify=config.get('verify_ssl', False)
        )
        
        if response.status_code == 200:
            libraries = response.json()["data"]
            print(f"SUCCESS: Found {len(libraries)} libraries")
            return libraries
        else:
            print(f"Failed to get libraries: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error getting libraries: {e}")
        return None

def get_workspaces(config, token_info, library_id):
    """Get workspaces for a specific library"""
    
    workspaces_url = f"{config['server'].rstrip('/')}/work/api/v2/customers/{config['customer_id']}/libraries/{library_id}/workspaces"
    headers = {
        'Authorization': f"{token_info['token_type']} {token_info['access_token']}",
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Getting workspaces for library: {library_id}")
        print(f"Request URL: {workspaces_url}")
        
        response = requests.get(
            workspaces_url, 
            headers=headers, 
            timeout=30,
            verify=config.get('verify_ssl', False)
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            workspaces_data = response.json()
            workspaces = workspaces_data.get("data", [])
            print(f"SUCCESS: Found {len(workspaces)} workspaces in library {library_id}")
            return workspaces
        else:
            print(f"Failed to get workspaces: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting workspaces: {e}")
        return None

def display_workspaces(library_id, workspaces):
    """Display workspaces information"""
    
    if not workspaces:
        print(f"No workspaces found in library {library_id}")
        return
    
    print(f"\nWorkspaces in Library '{library_id}':")
    print("=" * 60)
    
    for i, workspace in enumerate(workspaces, 1):
        workspace_id = workspace.get('id', 'N/A')
        workspace_name = workspace.get('name', 'N/A')
        workspace_type = workspace.get('type', 'N/A')
        is_active = workspace.get('is_active', True)
        description = workspace.get('description', 'No description')
        
        print(f"{i}. ID: {workspace_id}")
        print(f"   Name: {workspace_name}")
        print(f"   Type: {workspace_type}")
        print(f"   Status: {'Active' if is_active else 'Inactive'}")
        print(f"   Description: {description}")
        print("-" * 40)

def get_all_workspaces(config, token_info, libraries):
    """Get workspaces from all libraries"""
    
    all_workspaces = {}
    total_workspaces = 0
    
    print("\nGetting workspaces from all libraries...")
    print("=" * 50)
    
    for library in libraries:
        library_id = library.get('id')
        is_hidden = library.get('is_hidden', False)
        
        if is_hidden:
            print(f"\nSkipping hidden library: {library_id}")
            continue
        
        print(f"\n--- Library: {library_id} ---")
        
        workspaces = get_workspaces(config, token_info, library_id)
        
        if workspaces:
            all_workspaces[library_id] = workspaces
            total_workspaces += len(workspaces)
            display_workspaces(library_id, workspaces)
        else:
            print(f"No workspaces retrieved for library: {library_id}")
    
    print(f"\n" + "=" * 50)
    print("WORKSPACES SUMMARY")
    print("=" * 50)
    print(f"Total libraries checked: {len([lib for lib in libraries if not lib.get('is_hidden')])}")
    print(f"Total workspaces found: {total_workspaces}")
    
    for lib_id, workspaces in all_workspaces.items():
        print(f"  {lib_id}: {len(workspaces)} workspaces")
    
    return all_workspaces

def save_workspaces_to_file(all_workspaces, customer_id):
    """Save all workspaces data to JSON file"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"customer_{customer_id}_workspaces_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(all_workspaces, f, indent=2)
        
        print(f"\nWorkspaces data saved to: {filename}")
        
    except Exception as e:
        print(f"WARNING: Could not save workspaces to file - {e}")

def main():
    """Main function"""
    print("iManage Workspaces Retrieval")
    print("=" * 40)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Step 1: Get access token
    token_info = get_access_token(config)
    if not token_info:
        print("FAILED: Could not authenticate")
        return
    
    # Step 2: Get customer libraries
    print("\nGetting customer libraries...")
    libraries = get_customer_libraries(config, token_info)
    if not libraries:
        print("FAILED: Could not get libraries")
        return
    
    # Display libraries
    print("\nAvailable Libraries:")
    print("-" * 30)
    for lib in libraries:
        visibility = "Hidden" if lib.get('is_hidden') else "Visible"
        print(f"{lib['id']} | {lib['type']} | {visibility}")
    
    # Step 3: Get workspaces from all libraries
    all_workspaces = get_all_workspaces(config, token_info, libraries)
    
    # Step 4: Save results to file
    if all_workspaces:
        save_workspaces_to_file(all_workspaces, config['customer_id'])
        print("\nOperation completed successfully!")
    else:
        print("\nNo workspaces found in any library")

if __name__ == "__main__":
    main()

# test_custom_upload.py

import requests
import json

def test_single_custom_record():
    """Test creating a single custom record"""
    
    # Configuration
    config = {
        'server': 'https://your-imanage-server.com',
        'username': 'your_username',
        'password': 'your_password',
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
        'scope': 'openid profile email',
        'customer_id': 'your_customer_id',
        'library_id': 'ACTIVE',
        'custom_table': 'custom1'
    }
    
    # Get access token
    token_url = f"{config['server']}/auth/oauth2/token"
    token_data = {
        'grant_type': 'password',
        'username': config['username'],
        'password': config['password'],
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'scope': config['scope']
    }
    
    try:
        # Authenticate
        auth_response = requests.post(token_url, data=token_data)
        if auth_response.status_code != 200:
            print(f"Authentication failed: {auth_response.status_code}")
            return False
        
        access_token = auth_response.json()['access_token']
        print("Authentication successful")
        
        # Create custom record
        custom_url = f"{config['server']}/work/api/v2/customers/{config['customer_id']}/libraries/{config['library_id']}/customs/{config['custom_table']}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Sample custom record data
        custom_data = {
            'description': 'Test Document System',
            'enabled': 'true',
            'hipaa': 'false',
            'id': 'TEST001'
        }
        
        print(f"Creating custom record at: {custom_url}")
        print(f"Data: {json.dumps(custom_data, indent=2)}")
        
        response = requests.post(custom_url, json=custom_data, headers=headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [200, 201]:
            print("SUCCESS: Custom record created!")
            return True
        else:
            print("FAILED: Could not create custom record")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_single_custom_record()

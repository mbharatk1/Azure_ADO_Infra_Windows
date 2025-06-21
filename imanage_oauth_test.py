# imanage_oauth_test.py

import requests
import json
import os
from datetime import datetime

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_fields = ['server', 'username', 'password', 'client_id', 'client_secret']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required config fields: {missing_fields}")
        
        return config
    except FileNotFoundError:
        print(f"ERROR: Config file '{config_file}' not found!")
        print("Please create config.json with your iManage credentials.")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in '{config_file}'")
        return None

def get_access_token(config):
    """Get OAuth2 access token from iManage"""
    
    print("Getting OAuth2 access token...")
    print(f"Server: {config['server']}")
    print(f"Client ID: {config['client_id']}")
    print(f"Username: {config['username']}")
    print()
    
    # OAuth2 token endpoint
    token_url = f"{config['server'].rstrip('/')}/auth/oauth2/token"
    
    # OAuth2 token request data with scope
    token_data = {
        'grant_type': 'password',
        'username': config['username'],
        'password': config['password'],
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'scope': config.get('scope', 'openid profile email')  # Default scope if not specified
    }
    
    try:
        print(f"Making request to: {token_url}")
        print(f"Scope: {token_data['scope']}")
        
        response = requests.post(
            token_url,
            data=token_data,  # OAuth2 typically uses form data, not JSON
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_response = response.json()
            
            access_token = token_response.get('access_token')
            token_type = token_response.get('token_type', 'Bearer')
            expires_in = token_response.get('expires_in')
            scope = token_response.get('scope')
            
            if access_token:
                print("SUCCESS: Access token received!")
                print(f"Token Type: {token_type}")
                print(f"Expires in: {expires_in} seconds" if expires_in else "Expiration: Not specified")
                print(f"Granted Scope: {scope}" if scope else "Scope: Not specified")
                print(f"Access Token: {access_token[:20]}...{access_token[-10:]}")
                
                return {
                    'access_token': access_token,
                    'token_type': token_type,
                    'expires_in': expires_in,
                    'scope': scope,
                    'received_at': datetime.now().isoformat()
                }
            else:
                print("ERROR: No access token in response")
                print(f"Response: {json.dumps(token_response, indent=2)}")
                return None
        else:
            print(f"ERROR: Authentication failed")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Provide specific error guidance
            if response.status_code == 400:
                print("Possible issues: Invalid client credentials, grant type, or scope")
            elif response.status_code == 401:
                print("Possible issues: Invalid username/password or client_id/client_secret")
            elif response.status_code == 404:
                print("Possible issues: Wrong OAuth2 endpoint URL")
            
            return None
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server")
        print("Check your server URL and network connectivity")
        return None
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
        print("Server may be slow or unreachable")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed - {e}")
        return None
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON response from server")
        print(f"Response content: {response.text}")
        return None

def test_token_usage(config, token_info):
    """Test using the access token to make an API call"""
    
    if not token_info:
        return False
    
    print("\nTesting access token usage...")
    
    # Example API call using the token
    test_url = f"{config['server'].rstrip('/')}/work/api/v2/libraries"
    
    headers = {
        'Authorization': f"{token_info['token_type']} {token_info['access_token']}",
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(test_url, headers=headers, timeout=30)
        
        print(f"API Test Status: {response.status_code}")
        
        if response.status_code == 200:
            libraries = response.json().get('data', [])
            print(f"SUCCESS: API call successful!")
            print(f"Found {len(libraries)} libraries:")
            
            for lib in libraries[:5]:  # Show first 5 libraries
                print(f"   - {lib.get('id', 'N/A')}: {lib.get('name', 'N/A')}")
            
            return True
        else:
            print(f"API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"API test failed: {e}")
        return False

def main():
    """Main function"""
    print("iManage OAuth2 Connection Test")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Get access token
    token_info = get_access_token(config)
    
    if token_info:
        # Test the token
        api_success = test_token_usage(config, token_info)
        
        print("\n" + "=" * 50)
        if api_success:
            print("OVERALL TEST: PASSED")
            print("Your iManage OAuth2 connection is working!")
        else:
            print("OVERALL TEST: PARTIAL SUCCESS")
            print("Token received but API test failed")
        print("=" * 50)
        
        # Save token info for reference
        with open(f"token_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(token_info, f, indent=2)
        print("Token info saved to file for reference")
        
    else:
        print("\n" + "=" * 50)
        print("OVERALL TEST: FAILED")
        print("Could not obtain access token")
        print("=" * 50)

if __name__ == "__main__":
    main()

==================================
config.json
==================================
{
    "server": "https://your-imanage-server.com",
    "username": "your_username",
    "password": "your_password",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "scope": "openid profile email"
}

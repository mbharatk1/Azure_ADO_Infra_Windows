# imanage_custom_upload.py

import requests
import json
import csv
import os
import sys
from datetime import datetime

class iManageCustomUploader:
    def __init__(self, config):
        self.server = config['server'].rstrip('/')
        self.customer_id = config['customer_id']
        self.library_id = config['library_id']
        self.custom_table = config['custom_table']
        self.input_file_path = config['input_file_path']
        self.access_token = None
        self.headers = {}
        
    def authenticate(self, config):
        """Authenticate and get access token"""
        print("Authenticating with iManage...")
        
        token_url = f"{self.server}/auth/oauth2/token"
        token_data = {
            'grant_type': 'password',
            'username': config['username'],
            'password': config['password'],
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'scope': config.get('scope', 'openid profile email')
        }
        
        try:
            response = requests.post(token_url, data=token_data, timeout=30)
            
            if response.status_code == 200:
                token_response = response.json()
                self.access_token = token_response.get('access_token')
                
                if self.access_token:
                    self.headers = {
                        'Authorization': f"Bearer {self.access_token}",
                        'Content-Type': 'application/json'
                    }
                    print("SUCCESS: Authentication successful")
                    return True
                else:
                    print("ERROR: No access token received")
                    return False
            else:
                print(f"ERROR: Authentication failed - {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"ERROR: Authentication failed - {e}")
            return False
    
    def validate_file_path(self):
        """Validate that the input file exists and is accessible"""
        print(f"Validating file path: {self.input_file_path}")
        
        # Check if path is absolute
        if not os.path.isabs(self.input_file_path):
            print(f"ERROR: Path must be absolute - {self.input_file_path}")
            return False
        
        if not os.path.exists(self.input_file_path):
            print(f"ERROR: File not found - {self.input_file_path}")
            return False
        
        if not os.path.isfile(self.input_file_path):
            print(f"ERROR: Path is not a file - {self.input_file_path}")
            return False
        
        # Check file size
        file_size = os.path.getsize(self.input_file_path)
        if file_size == 0:
            print(f"ERROR: File is empty - {self.input_file_path}")
            return False
        
        print(f"SUCCESS: File found - {self.input_file_path} ({file_size} bytes)")
        return True
    
    def read_pipe_delimited_file(self):
        """Read pipe-delimited file and return records"""
        
        if not self.validate_file_path():
            return None
        
        print(f"Reading file: {self.input_file_path}")
        
        records = []
        try:
            with open(self.input_file_path, 'r', encoding='utf-8') as file:
                # Use csv.reader with pipe delimiter
                reader = csv.DictReader(file, delimiter='|')
                
                # Clean up field names (remove whitespace)
                if reader.fieldnames:
                    fieldnames = [field.strip() for field in reader.fieldnames]
                    print(f"Found fields: {fieldnames}")
                else:
                    print("ERROR: No headers found in file")
                    return None
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because header is row 1
                    # Clean up the row data
                    clean_row = {}
                    for key, value in row.items():
                        clean_key = key.strip() if key else f"field_{len(clean_row)}"
                        clean_value = value.strip() if value else ""
                        clean_row[clean_key] = clean_value
                    
                    # Skip empty rows
                    if any(clean_row.values()):
                        clean_row['_row_number'] = row_num
                        records.append(clean_row)
                
                print(f"Successfully read {len(records)} records")
                return records
                
        except Exception as e:
            print(f"ERROR: Failed to read file - {e}")
            return None
    
    def create_custom_record(self, record_data):
        """Create a single custom record"""
        
        # Build the API URL
        url = f"{self.server}/work/api/v2/customers/{self.customer_id}/libraries/{self.library_id}/customs/{self.custom_table}"
        
        # Remove internal fields that shouldn't be sent to API
        api_data = {k: v for k, v in record_data.items() if not k.startswith('_')}
        
        try:
            print(f"Creating custom record with ID: {api_data.get('id', 'N/A')} (Row {record_data.get('_row_number', 'N/A')})")
            
            response = requests.post(url, json=api_data, headers=self.headers, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"SUCCESS: Custom record created")
                return {
                    'status': 'success',
                    'record_id': api_data.get('id'),
                    'response': response.json() if response.content else None,
                    'row_number': record_data.get('_row_number')
                }
            else:
                print(f"ERROR: Failed to create record - {response.status_code}")
                print(f"Response: {response.text}")
                return {
                    'status': 'failed',
                    'record_id': api_data.get('id'),
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'row_number': record_data.get('_row_number')
                }
                
        except Exception as e:
            print(f"ERROR: Request failed - {e}")
            return {
                'status': 'failed',
                'record_id': api_data.get('id'),
                'error': str(e),
                'row_number': record_data.get('_row_number')
            }
    
    def process_bulk_upload(self):
        """Process bulk upload from configured file path"""
        
        print("Starting bulk custom records upload...")
        print("=" * 50)
        print(f"Configuration:")
        print(f"  Server: {self.server}")
        print(f"  Customer ID: {self.customer_id}")
        print(f"  Library ID: {self.library_id}")
        print(f"  Custom Table: {self.custom_table}")
        print(f"  Input File: {self.input_file_path}")
        print("-" * 50)
        
        # Read the file
        records = self.read_pipe_delimited_file()
        if not records:
            return None
        
        print(f"\nProcessing {len(records)} records...")
        print("-" * 30)
        
        results = []
        success_count = 0
        failure_count = 0
        
        for i, record in enumerate(records, 1):
            print(f"\nRecord {i}/{len(records)}:")
            result = self.create_custom_record(record)
            results.append(result)
            
            if result['status'] == 'success':
                success_count += 1
            else:
                failure_count += 1
            
            # Brief pause to avoid overwhelming the server
            if i < len(records):
                import time
                time.sleep(0.5)
        
        # Generate summary
        print("\n" + "=" * 50)
        print("UPLOAD SUMMARY")
        print("=" * 50)
        print(f"Source File: {self.input_file_path}")
        print(f"Total records: {len(records)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {failure_count}")
        print(f"Success rate: {(success_count/len(records)*100):.1f}%")
        
        # Save detailed results
        self.save_results(results)
        
        return results
    
    def save_results(self, results):
        """Save upload results to CSV file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"custom_upload_results_{timestamp}.csv"
        
        try:
            with open(results_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['row_number', 'record_id', 'status', 'error']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in results:
                    writer.writerow({
                        'row_number': result.get('row_number', ''),
                        'record_id': result.get('record_id', ''),
                        'status': result.get('status', ''),
                        'error': result.get('error', '')
                    })
            
            print(f"Results saved to: {results_file}")
            
        except Exception as e:
            print(f"WARNING: Could not save results file - {e}")

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_fields = [
            'server', 'username', 'password', 'client_id', 'client_secret',
            'customer_id', 'library_id', 'custom_table', 'input_file_path'
        ]
        
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required config fields: {missing_fields}")
        
        # Validate that input_file_path is a string (not array)
        if not isinstance(config['input_file_path'], str):
            raise ValueError("input_file_path must be a string (absolute path to single file)")
        
        # Validate that path is absolute
        if not os.path.isabs(config['input_file_path']):
            raise ValueError(f"input_file_path must be absolute path: {config['input_file_path']}")
        
        return config
    except FileNotFoundError:
        print(f"ERROR: Config file '{config_file}' not found!")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in '{config_file}'")
        return None
    except ValueError as e:
        print(f"ERROR: Configuration validation failed - {e}")
        return None

def main():
    """Main function"""
    print("iManage Custom Records Upload")
    print("=" * 40)
    
    # Allow config file to be passed as command line argument
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    
    # Load configuration
    config = load_config(config_file)
    if not config:
        return
    
    # Initialize uploader
    uploader = iManageCustomUploader(config)
    
    # Authenticate
    if not uploader.authenticate(config):
        print("FAILED: Could not authenticate")
        return
    
    # Process upload
    results = uploader.process_bulk_upload()
    
    if results:
        print("\nUpload completed!")
    else:
        print("\nUpload failed!")

if __name__ == "__main__":
    main()

================================================
Configuration File (config.json)
{
    "server": "https://your-imanage-server.com",
    "username": "your_username",
    "password": "your_password",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "scope": "openid profile email",
    "customer_id": "your_customer_id",
    "library_id": "ACTIVE",
    "custom_table": "custom1",
    "input_file_path": "C:\\data\\imanage\\custom1.txt"
}

======================================
custom1.txt

description|enabled|hipaa|id
Document Management System|true|false|DMS001
Email Archival Solution|true|true|EAS002
Contract Management|false|false|CM003
Legal Case Files|true|true|LCF004
HR Documentation|true|true|HR005


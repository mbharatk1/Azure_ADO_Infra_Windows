how to get a workspace and all of its folders. The program receives a workspace ID and a library ID, and it retrieves the associated workspace and all its folders.


# Getting a Workspace and all of its Folders
# Import the requests library.
import requests
 
# Authorize the API request by sending the X-Auth-Token,
# retrieved when logging in, as a header.
headers = {'X-Auth-Token': x_auth_token}

# Store the Work Server host name or DNS
server = 'HOSTNAME'

# Store the customer ID in a variable that is retrieved during logging in.
customer_id ='CUSTOMER_ID'

# Store the library ID in a variable.
library_id = 'LIBRARY_ID'

# Store the workspace ID in a variable.
workspace_id ='WORKSPACE_ID'

# recursive getFolder
def getFolder(folder_list, prefix):
    if len(folder_list) == 0:
        return
    else:
        for folder in folder_list:
            if folder['wstype'] == 'folder':
                print(prefix + folder['name'] + ' (' + folder['id'] + ')')
                if folder['has_subfolders'] == True:
                    response = requests.get('https://' + server + '/work/api/v2/customers/' + customer_id +
                            '/libraries/' + library_id + '/folders/' + folder['id'] +
                            '/children', headers=headers)
                    newprefix = prefix + '--'
                    getFolder(response.json()['data'], newprefix)

# Get the name of the workspace associated with the workspace_id.
# This will be used while displaying the output. The response is a string.
response = requests.get('https://' + server + '/work/api/v2/customers/' + customer_id +
                        '/libraries/'+ library_id + '/workspaces/' + workspace_id,
                        headers=headers)

# Check if the API request was successful.
if response.status_code == 200:
    # Retrieve the response in JSON format.
    json_response = response.json()
 
    # Get the name of the workspace.
    workspace_name = json_response['data']['name']

    # Get the child folders of this workspace.
    response = requests.get('https://' + server + '/work/api/v2/customers/' + customer_id +
                            '/libraries/'+ library_id + '/workspaces/' + workspace_id +
                            '/children', headers=headers)

    if response.status_code == 200:
        # Retrieve the response in JSON format.
        json_response = response.json()
        print ('The names and IDs of folders within workspace "' + workspace_name + '":\n')
        print ('-' + workspace_name)
        getFolder(json_response['data'], '|--')

else:
    # API request failed. Print the error message.
    print('Task failed.')
    json_response = response.json()
    print(json_response['error']['code_message'])

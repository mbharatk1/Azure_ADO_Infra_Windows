# Define authentication details
$x_auth_token = "your_x_auth_token"
$customer_id = "your_customer_id"
$server_name = "your_server_name"
$library_id = "your_library_id"
$workspace_id = "X"  # Workspace ID where folders will be created

# Define headers for API requests
$headers = @{
    "X-Auth-Token" = $x_auth_token
    "Content-Type" = "application/json"
}

# Define the target folder path (nested structure)
$target_folder_path = "folder1/folder11/folder111/folder1111/folder11111/folder1111111"

# Split folder path into individual levels
$folder_levels = $target_folder_path -split "/"

# Initialize the parent folder ID as the workspace
$parent_folder_id = $workspace_id

foreach ($folder in $folder_levels) {
    Write-Verbose " Checking existence of folder: $folder under parent $parent_folder_id"

    # API URL to check existing folders within the current parent folder
    $folder_check_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/folders?parent_id=$parent_folder_id"

    try {
        # Retrieve existing folders
        $existing_folders = Invoke-RestMethod -Uri $folder_check_url -Headers $headers -Method Get -Verbose -ErrorAction Stop

        # Check if folder already exists
        $existing_folder = $existing_folders.data | Where-Object { $_.name -eq $folder }

        if ($existing_folder) {
            Write-Host " Folder '$folder' already exists. Moving to the next level..."
            $parent_folder_id = $existing_folder.id  # Set parent ID for next iteration
        } else {
            Write-Host " Folder '$folder' is missing. Creating now..."

            # Define folder creation payload
            $payload = @{
                "name" = $folder
                "default_security" = "inherit"
                "parent_id" = $parent_folder_id
            } | ConvertTo-Json -Depth 3

            # API URL for folder creation
            $folder_create_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/workspaces/$workspace_id/folders"

            # Send POST request to create the folder
            $create_response = Invoke-RestMethod -Uri $folder_create_url -Headers $headers -Method Post -Body $payload -Verbose -ErrorAction Stop

            Write-Host " Folder '$folder' created successfully!"
            $parent_folder_id = $create_response.data.id  # Set new parent ID for next level
        }

    } catch {
        Write-Host " Error processing folder '$folder'"
        Write-Host " Error Details: $_"
        break  # Stop execution if a failure occurs
    }
}

Write-Host "🎉 All required folders have been created successfully!"

# Define required variables with actual values
$x_auth_token = "x_auth_token"  # Authentication token for API access
$customer_id = "customer_id"    # Customer ID associated with iManage Work
$server_name = "server"         # iManage Work Server name
$library_id = "library_id"      # Library ID where workspace exists
$workspace_id = "workspace_id"  # Workspace ID to create folder in

# Construct API URL to check permissions
$operations_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/workspaces/$workspace_id/operations"

# Define headers for API request
$headers = @{
    "X-Auth-Token" = $x_auth_token
}

try {
    Write-Verbose "🚀 Checking user permissions for workspace: $workspace_id"

    # Make GET request to verify workspace permissions
    $response = Invoke-RestMethod -Uri $operations_url -Headers $headers -Method Get -Verbose -ErrorAction Stop

    # Check if 'add_folders' permission is available
    if ($response.data.add_folders -eq $false) {
        Write-Host "❌ You do not have permission to add a folder. Exiting script."
        exit
    }

    Write-Host "✅ You have permissions to add a folder. Proceeding with creation..."

    # Define the folder creation payload
    $payload = @{
        "name" = "Confidential"
        "default_security" = "inherit"
        "profile" = @{
            "custom1_description" = "00100000001XD0Y"
            "custom2_description" = "177101"
        }
    } | ConvertTo-Json -Depth 3

    # Construct API URL for folder creation
    $folder_create_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/workspaces/$workspace_id/folders"

    # Define headers including content type
    $headers = @{
        "X-Auth-Token" = $x_auth_token
        "Content-Type" = "application/json"
    }

    Write-Verbose "📂 Creating folder in workspace: $workspace_id"

    # Send POST request to create folder
    $create_response = Invoke-RestMethod -Uri $folder_create_url -Headers $headers -Method Post -Body $payload -Verbose -ErrorAction Stop

    Write-Host "✅ Folder creation successful!"
    $create_response | ConvertTo-Json -Depth 3

} catch {
    Write-Host "🔥 An error occurred!"
    Write-Host "Error Message: $_"
    Write-Verbose "⚠️ Stack Trace: $($_.Exception.StackTrace)"
}

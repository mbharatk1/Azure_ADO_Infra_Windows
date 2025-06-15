# Define authentication details
$x_auth_token = "your_x_auth_token"
$customer_id = "your_customer_id"
$server_name = "your_server_name"
$library_id = "your_library_id"
$workspace_id = "your_workspace_id"

# Define headers for API requests
$headers = @{
    "X-Auth-Token" = $x_auth_token
    "Content-Type" = "application/json"
}

# Step 1️⃣: Retrieve workspace profile to check existing attributes
$workspace_profile_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/workspaces/$workspace_id"

Write-Verbose "🔍 Fetching workspace details for $workspace_id..."
try {
    $workspace_details = Invoke-RestMethod -Uri $workspace_profile_url -Headers $headers -Method Get -Verbose -ErrorAction Stop
    Write-Host "✅ Workspace details retrieved successfully!"
    Write-Host "📌 Available attributes: $($workspace_details.data | ConvertTo-Json -Depth 3)"
} catch {
    Write-Host "🔥 Error retrieving workspace details!"
    Write-Host "⚠️ Error Message: $_"
    exit
}

# Step 2️⃣: Check permissions for modifying workspace attributes
$permissions_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/workspaces/$workspace_id/operations"
Write-Verbose "🔑 Checking workspace modification permissions..."
try {
    $permissions = Invoke-RestMethod -Uri $permissions_url -Headers $headers -Method Get -Verbose -ErrorAction Stop
    if ($permissions.data.modify -eq $false) {
        Write-Host "❌ Modification not allowed. You lack permissions to update attributes."
        exit
    }
    Write-Host "✅ You have permission to modify workspace attributes!"
} catch {
    Write-Host "🔥 Error retrieving modification permissions!"
    Write-Host "⚠️ Error Message: $_"
    exit
}

# Step 3️⃣: Attempt to update multiple attributes
$payload = @{
    "profile" = @{
        "author" = "New_Author_Name"
        "owner" = "New_Owner_Name"
        "default_security" = "public"
    }
} | ConvertTo-Json -Depth 3

$update_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/workspaces/$workspace_id"

Write-Verbose "🔄 Attempting to update multiple fields (Author, Owner, Security)..."
try {
    $update_response = Invoke-RestMethod -Uri $update_url -Headers $headers -Method Patch -Body $payload -Verbose -ErrorAction Stop
    Write-Host "✅ Workspace attributes updated successfully!"
    Write-Host "🔄 Updated workspace details: $($update_response | ConvertTo-Json -Depth 3)"
} catch {
    Write-Host "🔥 Error updating workspace attributes!"
    Write-Host "⚠️ Error Message: $_"
}

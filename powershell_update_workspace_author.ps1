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

# 1️⃣ Retrieve workspace profile to check existing attributes
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

# 2️⃣ Attempt to update the 'author' field
$payload = @{
    "profile" = @{
        "author" = "New_Author_Name"
    }
} | ConvertTo-Json -Depth 3

$update_url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_id/workspaces/$workspace_id"

Write-Verbose "🔄 Attempting to update the author field..."
try {
    $update_response = Invoke-RestMethod -Uri $update_url -Headers $headers -Method Patch -Body $payload -Verbose -ErrorAction Stop
    Write-Host "✅ Author updated successfully!"
    Write-Host "🔄 Updated workspace details: $($update_response | ConvertTo-Json -Depth 3)"
} catch {
    Write-Host "🔥 Error updating author field!"
    Write-Host "⚠️ Error Message: $_"
}

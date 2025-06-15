# Define required variables with placeholder values
$x_auth_token = "x_auth_token"    # Authentication token for API access
$customer_id = "customer_id"      # Customer ID associated with iManage Work
$server_name = "server"           # Server name of iManage Work instance
$library_Id = "library_Id"        # Library ID where workspace exists
$workspace_Id = "workspace_Id"    # Workspace ID we want to retrieve

# Construct the API URL dynamically
$url = "https://$server_name/work/api/v2/customers/$customer_id/libraries/$library_Id/workspaces/$workspace_Id"

# Define headers required for the API request
$headers = @{
    "X-Auth-Token" = $x_auth_token  # Authentication header
}

# Try executing the API request with verbose logging
try {
    Write-Verbose " Sending API request to: $url"
    
    # Invoke the API request with verbose mode and error stopping
    $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -Verbose -ErrorAction Stop

    Write-Verbose " API request successful. Checking response..."

    # Check if response contains valid data
    if ($response -ne $null) {
        Write-Host "Operation successful"

        # Check if 'data' exists in the API response
        if ($response.PSObject.Properties["data"] -ne $null) {
            $result = $response.data
            Write-Host " The JSON structure for workspace Id: $($result.name)"
            $result | ConvertTo-Json -Depth 4
        } else {
            Write-Host " No records found."
        }
    } else {
        Write-Host " Operation unsuccessful"
        $response | ConvertTo-Json -Depth 4
    }

} catch {
    # Capture and display any errors that occur during execution with verbose details
    Write-Host " An error occurred while making the API request!"
    Write-Host "Error Message: $_"
    Write-Verbose " Stack Trace: $($_.Exception.StackTrace)"
}

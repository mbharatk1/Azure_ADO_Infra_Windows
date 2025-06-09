<#  
    Purpose:  
    This PowerShell script updates the comments of an existing document in iManage Work using the Universal API.  
    It authenticates via OAuth2, retrieves the document ID, and updates the comments using a PATCH request.  

    **Prerequisites:**  
    1. **PowerShell Version:** Ensure PowerShell 7 or later is installed.  
    2. **Network Access:** Ensure outbound HTTPS access to iManage API.  
    3. **API Credentials:** Obtain Client ID, Secret, Username, and Password.  
    4. **Install Required Modules:** Ensure `Invoke-RestMethod` is available.  
    5. **Run Script:** Execute from PowerShell after setting credentials in `params.txt`.  
#>

# Define parameter file path
$paramFile = "C:\Config\params.txt"

# Read the parameter file
$parameters = @{}
Get-Content $paramFile | ForEach-Object {
    $key, $value = $_.Split("=")
    $parameters[$key.Trim()] = $value.Trim()
}

# Extract parameters
$username = $parameters["username"]
$password = $parameters["password"]
$clientId = $parameters["client_id"]
$clientSecret = $parameters["client_secret"]
$workServer = $parameters["work_server"]
$customerId = "1"  # Update as needed
$libraryId = "CH"  # Update as needed
$documentId = "12345"  # Replace with actual document ID
$logFile = "C:\Logs\iManage_API_Log.txt"

# Function for logging
Function Write-Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - $message"
}

Write-Log "Starting document comments update script..."

# Step 1: Authenticate with iManage Work API
try {
    Write-Log "Requesting OAuth Token..."
    $authBody = @{
        "username"     = $username
        "password"     = $password
        "grant_type"   = "password"
        "client_id"    = $clientId
        "client_secret"= $clientSecret
        "scope"        = "admin"
    }
    
    $authResponse = Invoke-RestMethod -Method Post -Uri "https://$workServer/auth/oauth2/token" -Body $authBody -ContentType "application/x-www-form-urlencoded"
    $accessToken = $authResponse.access_token
    Write-Log "OAuth Token retrieved successfully."
}
catch {
    Write-Log "ERROR: Failed to retrieve OAuth Token - $_"
    Exit 1
}

# Step 2: Validate if Document Exists
$documentCheckUrl = "https://$workServer/work/api/v2/customers/$customerId/libraries/$libraryId/documents/$documentId"

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Accept"        = "application/json"
}

try {
    Write-Log "Checking if document exists..."
    $documentCheckResponse = Invoke-RestMethod -Uri $documentCheckUrl -Method Get -Headers $headers
    Write-Log "Document found: $documentId"
}
catch {
    Write-Log "ERROR: Document ID $documentId not found - $_"
    Write-Output "ERROR: Document ID $documentId does not exist."
    Exit 1
}

# Step 3: Update Document Comments
$updateUrl = "https://$workServer/work/api/v2/customers/$customerId/libraries/$libraryId/documents/$documentId"
$updateBody = @{
    "comments" = "Updated comments for the document."
}

$headers["Content-Type"] = "application/json"

try {
    Write-Log "Updating document comments..."
    $response = Invoke-RestMethod -Uri $updateUrl -Method Patch -Headers $headers -Body ($updateBody | ConvertTo-Json) -ContentType "application/json"
    Write-Log "Document comments updated successfully."
    Write-Output "Document comments updated successfully."
}
catch {
    Write-Log "ERROR: Failed to update document comments - $_"
    Write-Output "ERROR: Unable to update comments for document ID $documentId."
    Exit 1
}

Write-Log "Script execution completed successfully."
Write-Host "-------------------`nPress Enter to exit`n-------------------"
Read-Host

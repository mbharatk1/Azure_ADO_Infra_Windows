<#  
    Purpose:  
    This PowerShell script updates the comments of multiple documents in iManage Work using the Universal API.  
    It retrieves document IDs dynamically based on names from a CSV file and updates their comments in bulk.  

    **Prerequisites:**  
    1. **PowerShell Version:** Ensure PowerShell 7 or later is installed.  
    2. **Network Access:** Ensure outbound HTTPS access to iManage API.  
    3. **API Credentials:** Obtain Client ID, Secret, Username, and Password.  
    4. **CSV File:** Create a CSV file (`C:\Config\documents.csv`) with the format:
       ```
       DocumentName,NewComment
       SampleDocument1,Updated comment 1
       SampleDocument2,Updated comment 2
       ```
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
$customerId = $parameters["customer_id"]
$libraryId = $parameters["library_id"]
$datafile = "C:\Config\documents.csv"
$logFile = "C:\Logs\iManage_API_Log.txt"

# Function for logging
Function Write-Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - $message"
}

Write-Log "Starting batch document comments update script..."

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

# Step 2: Validate CSV File
if (-Not (Test-Path $datafile)) {
    Write-Log "ERROR: CSV file not found at $datafile"
    Exit 1
}

# Step 3: Process Each Document in CSV File
Write-Log "Processing batch updates..."
Import-CSV $datafile -Header "DocumentName", "NewComment" | ForEach-Object {
    $documentName = $_.DocumentName
    $newComment = $_.NewComment

    # Step 4: Retrieve Document ID
    $searchUrl = "https://$workServer/work/api/v2/customers/$customerId/libraries/$libraryId/documents/searches"
    $searchBody = @{
        "filters" = @{
            "name" = $documentName
        }
    }

    $headers = @{
        "Authorization" = "Bearer $accessToken"
        "Accept"        = "application/json"
        "Content-Type"  = "application/json"
    }

    try {
        Write-Log "Searching for document ID for '$documentName'..."
        $searchResponse = Invoke-RestMethod -Uri $searchUrl -Method Post -Headers $headers -Body ($searchBody | ConvertTo-Json) -ContentType "application/json"
        
        if ($searchResponse.documents.Count -eq 0) {
            Write-Log "ERROR: No document found with name '$documentName'."
            Write-Output "ERROR: Document '$documentName' does not exist."
            return
        }

        $documentId = $searchResponse.documents[0].id
        Write-Log "Document ID retrieved for '$documentName': $documentId"
    }
    catch {
        Write-Log "ERROR: Failed to retrieve document ID for '$documentName' - $_"
        return
    }

    # Step 5: Update Document Comments
    $updateUrl = "https://$workServer/work/api/v2/customers/$customerId/libraries/$libraryId/documents/$documentId"
    $updateBody = @{
        "comments" = $newComment
    }

    try {
        Write-Log "Updating comments for document '$documentName'..."
        $response = Invoke-RestMethod -Uri $updateUrl -Method Patch -Headers $headers -Body ($updateBody | ConvertTo-Json) -ContentType "application/json"
        Write-Log "Successfully updated comments for document '$documentName' (ID: $documentId)."
        Write-Output "Successfully updated comments for document '$documentName'."
    }
    catch {
        Write-Log "ERROR: Failed to update document comments for '$documentName' - $_"
        Write-Output "ERROR: Unable to update comments for document '$documentName'."
    }
}

Write-Log "Batch document comments update completed successfully."
Write-Host "-------------------`nPress Enter to exit`n-------------------"
Read-Host

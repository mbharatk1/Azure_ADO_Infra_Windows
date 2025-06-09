<#  
    Purpose:  
    This PowerShell script updates the comments of an existing document in iManage Work using the Universal API.  
    It dynamically retrieves the document ID based on its name before updating its metadata.  

    **Prerequisites:**  
    1. **PowerShell Version:** Ensure PowerShell 7 or later is installed.  
       Check version using:
       ```powershell
       $PSVersionTable.PSVersion
       ```
       Install latest version from [Microsoft PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell).

    2. **Network Access & Firewall Configuration:**  
       - Ensure outbound HTTPS access to iManage Work API:
         ```
         https://xxxxx-mobility.imanage.work/api
         https://xxxxx-mobility.imanage.work/auth/oauth2/token
         ```
       - If restricted, update firewall/proxy settings.

    3. **API Credentials:**  
       - Obtain credentials from **iManage Control Center**:
         - **Client ID & Secret**
         - **Admin Username & Password**
         - **Library ID & Customer ID**
       - Store credentials securely in a **parameter file (`params.txt`)**.

    4. **Required PowerShell Modules:**  
       - Ensure REST API calls are supported:
         ```powershell
         Get-Command Invoke-RestMethod
         ```
       - If missing, install:
         ```powershell
         Install-Module PowerShellGet -Force
         ```

    **Sample `params.txt` file (stored in `C:\Config\params.txt`)**:
    ---------------------------------------------------
    username=admin
    password=yourpassword
    client_id=CLIENT123
    client_secret=SECRET456
    work_server=your-imanage-instance.com
    customer_id=1
    library_id=CH
    document_name=SampleDocument
    ---------------------------------------------------

    **Steps to Execute the Script:**
    1. **Prepare Environment:**  
       - Ensure API credentials are stored in `params.txt`.
       - Confirm network access to iManage Work API.

    2. **Run Script:**  
       - Open **PowerShell as Administrator**.
       - Navigate to the script directory:
         ```powershell
         cd C:\Scripts
         ```
       - Execute the script:
         ```powershell
         .\imanage_update_document.ps1
         ```

    3. **Confirm Execution:**  
       - The script will search for the document and display the ID.
       - If found, it will proceed with the update; otherwise, an error message is displayed.

    4. **View Logs & Errors:**  
       - Check **C:\Logs\iManage_API_Log.txt** for execution details.
       - If errors occur, verify API credentials, network settings, or document existence.
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
$documentName = $parameters["document_name"]
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

# Step 2: Search for the Document ID
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
    Write-Log "Searching for document ID..."
    $searchResponse = Invoke-RestMethod -Uri $searchUrl -Method Post -Headers $headers -Body ($searchBody | ConvertTo-Json) -ContentType "application/json"
    
    if ($searchResponse.documents.Count -eq 0) {
        Write-Log "ERROR: No document found with name $documentName."
        Write-Output "ERROR: Document '$documentName' does not exist."
        Exit 1
    }

    $documentId = $searchResponse.documents[0].id
    Write-Log "Document ID retrieved: $documentId"
}
catch {
    Write-Log "ERROR: Failed to retrieve document ID - $_"
    Exit 1
}

# Step 3: Update Document Comments
$updateUrl = "https://$workServer/work/api/v2/customers/$customerId/libraries/$libraryId/documents/$documentId"
$updateBody = @{
    "comments" = "Updated comments for the document."
}

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

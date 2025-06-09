<#  
    Purpose:  
    This PowerShell script updates **custom29** and **custom30** metadata fields for a list of workspaces in iManage Work.  
    It reads credentials from a parameter file, authenticates using OAuth2, retrieves workspace details, and applies updates from a CSV file.  
    The script includes **logging, validation, and error handling** for smooth execution.

    **Prerequisites:**  
    1. **PowerShell Version:** Ensure PowerShell 7 or later is installed.  
       Check version using:
       ```powershell
       $PSVersionTable.PSVersion
       ```
       Install latest version from [Microsoft PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell).

    2. **Network Access & Firewall Configuration:**  
       - Allow outbound HTTPS requests to iManage Work API:
         ```
         https://xxxxx-mobility.imanage.work/api
         https://xxxxx-mobility.imanage.work/auth/oauth2/token
         ```
       - If restricted, update firewall/proxy settings.

    3. **API Credentials:** (Control Center)  
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

    5. **CSV File for Workspace Metadata Updates:**  
       - Create a CSV file (`C:\Config\workspace_updates.csv`) with the format:
         ```
         WorkspaceID,Custom29_Value,Custom30_Value
         12345,Value1,Value2
         67890,AnotherValue1,AnotherValue2
         ```

    6. **Script Execution Policy:**  
       - If blocked, allow script execution:
         ```powershell
         Set-ExecutionPolicy Unrestricted -Scope Process
         ```

    **Steps to Execute the Script:**
    1. **Prepare Environment:**  
       - Ensure API credentials are stored in `params.txt`.
       - Verify CSV file `workspace_updates.csv` exists.
       - Confirm internet access to iManage Work API.

    2. **Run Script:**  
       - Open **PowerShell as Administrator**.
       - Navigate to the script directory:
         ```powershell
         cd C:\Scripts
         ```
       - Execute the script:
         ```powershell
         .\imanage_update_custom_metadata.ps1
         ```

    3. **Confirm Execution:**  
       - The script will display the list of workspaces being updated.
       - Enter **Y** to proceed or **N** to cancel.

    4. **View Logs & Errors:**  
       - Check **C:\Logs\iManage_API_Log.txt** for execution details.
       - If errors occur, verify API credentials, network settings, or CSV file format.
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
$server = $parameters["work_server"]
$library = $parameters["library"]
$datafile = "C:\Config\workspace_updates.csv"

# Log file location
$logFile = "C:\Logs\iManage_API_Log.txt"

# Function for logging
Function Write-Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - $message"
}

Write-Log "Starting workspace metadata update script..."

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
    
    $authResponse = Invoke-RestMethod -Method Post -Uri "https://$server/auth/oauth2/token" -Body $authBody -ContentType "application/x-www-form-urlencoded"
    $accessToken = $authResponse.access_token
    Write-Log "OAuth Token retrieved successfully."
}
catch {
    Write-Log "ERROR: Failed to retrieve OAuth Token - $_"
    Exit 1
}

# Step 2: Get Customer ID
try {
    Write-Log "Fetching Customer ID..."
    $customerResponse = Invoke-RestMethod -Method Get -Uri "https://$server/api" -Headers @{ "Authorization" = "Bearer $accessToken" }
    $customerId = $customerResponse.data.user.customer_id
    Write-Log "Customer ID retrieved: $customerId"
}
catch {
    Write-Log "ERROR: Failed to retrieve Customer ID - $_"
    Exit 1
}

# Step 3: Validate CSV File
if (-Not (Test-Path $datafile)) {
    Write-Log "ERROR: CSV file not found at $datafile"
    Exit 1
}

# Step 4: Confirm before updating workspaces
Get-Content $datafile
$confirm = Read-Host -Prompt "---------------------------------------------`nYou are about to update custom29 and custom30 metadata. `nEnter Y to proceed, N to cancel.`n---------------------------------------------"

if ($confirm -ne "Y") {
    Write-Log "User canceled the operation."
    Exit 1
}

# Step 5: Update Workspace Metadata
try {
    Write-Log "Updating workspace metadata..."
    Import-CSV $datafile -Header "id", "custom29", "custom30" | ForEach-Object {
        $payload = @{
            "profile" = @{
                "custom29" = $_.custom29
                "custom30" = $_.custom30
            }
        }
        
        $workspaceUri = "https://$server/api/v2/customers/$customerId/libraries/$library/workspaces/$($_.id)"
        $response = Invoke-RestMethod -Method Patch -Uri $workspaceUri -Headers @{ 
            "Authorization" = "Bearer $accessToken"
            "Content-Type" = "application/json" 
        } -Body ($payload | ConvertTo-Json)
        
        Write-Log "Successfully updated workspace: $($_.id)"
    }
}
catch {
    Write-Log "ERROR: Failed to update workspace metadata - $_"
    Exit 1
}

Write-Log "Workspace metadata update completed successfully."

# Step 6: Sign Out
try {
    $signOutUri = "https://$server/login/terminate"
    Invoke-RestMethod -Method Get -Uri $signOutUri -Headers @{ "Authorization" = "Bearer $accessToken" }
    Write-Log "Sign out successful."
}
catch {
    Write-Log "ERROR: Sign out unsuccessful - $_"
}

Write-Log "Script execution completed successfully."
Write-Host "-------------------`nPress Enter to exit`n-------------------"
Read-Host

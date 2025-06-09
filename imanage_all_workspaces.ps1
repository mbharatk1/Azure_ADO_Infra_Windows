<#  
    Purpose:  
    This PowerShell script retrieves all workspaces from iManage Work, including their IDs, Matter Classes,  
    and custom attributes. It organizes the output hierarchically by Matter Class and Workspace.

    **Prerequisites:**  
    1. Ensure you have **PowerShell 7 or later** installed.  
    2. Obtain **API credentials** (client ID, client secret, username, password).  
    3. Ensure **network access** to iManage Work API.  
    4. Create and save `params.txt` with credentials in `C:\Config\params.txt`.  
    5. Set execution policy if needed:
       ```powershell
       Set-ExecutionPolicy Unrestricted -Scope Process
       ```
    6. Run the script using:
       ```powershell
       .\imanage_list_workspaces.ps1
       ```
#>

# Define the parameter file path
$paramFile = "C:\Config\params.txt"

# Read the parameter file and convert to a Hashtable
$parameters = @{}

Get-Content $paramFile | ForEach-Object {
    $key, $value = $_.Split("=")
    $parameters[$key.Trim()] = $value.Trim()
}

# Extract parameters for use in the script
$username = $parameters["username"]
$password = $parameters["password"]
$clientId = $parameters["client_id"]
$clientSecret = $parameters["client_secret"]
$workServer = $parameters["work_server"]

# Define iManage authentication URL
$oauthUri = "https://$workServer/auth/oauth2/token"

# Log file location
$logFile = "C:\Logs\iManage_API_Log.txt"

# Function to log messages with timestamp
Function Write-Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - $message"
}

Write-Log "Starting iManage workspace retrieval..."

# Authenticate and retrieve OAuth Token
$authBody = @{
    "username"     = $username
    "password"     = $password
    "grant_type"   = "password"
    "client_id"    = $clientId
    "client_secret"= $clientSecret
    "scope"        = "admin"
}

try {
    Write-Log "Requesting OAuth Token..."
    $tokenResponse = Invoke-RestMethod -Uri $oauthUri -Method Post -Body $authBody -ContentType "application/x-www-form-urlencoded"
    $accessToken = $tokenResponse.access_token
    Write-Log "OAuth Token retrieved successfully."
}
catch {
    Write-Log "ERROR: Failed to retrieve OAuth Token - $_"
    Exit 1
}

# Define API endpoint to get all workspaces
$workspaceUrl = "https://$workServer/work/api/v2/customers/1/libraries/CH/workspaces"

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Accept"        = "application/json"
}

try {
    Write-Log "Fetching workspace details..."
    $workspaceResponse = Invoke-RestMethod -Uri $workspaceUrl -Method Get -Headers $headers
    Write-Log "Workspace details retrieved successfully."
}
catch {
    Write-Log "ERROR: Failed to retrieve workspace details - $_"
    Exit 1
}

# Organize workspaces by Matter Class
$workspaceHierarchy = @{}

foreach ($workspace in $workspaceResponse) {
    $matterClass = $workspace.custom2  # Assuming 'custom2' holds Matter Class
    $workspaceId = $workspace.id
    $workspaceName = $workspace.name
    $customAttributes = $workspace | Select-Object -Property *

    if (-not $workspaceHierarchy[$matterClass]) {
        $workspaceHierarchy[$matterClass] = @()
    }

    $workspaceHierarchy[$matterClass] += @{
        "Workspace Name" = $workspaceName
        "Workspace ID" = $workspaceId
        "Custom Attributes" = $customAttributes
    }
}

# Display hierarchical output
foreach ($matterClass in $workspaceHierarchy.Keys) {
    Write-Output "Matter Class: $matterClass"
    foreach ($workspace in $workspaceHierarchy[$matterClass]) {
        Write-Output "  Workspace: $($workspace.'Workspace Name')"
        Write-Output "    ID: $($workspace.'Workspace ID')"
        Write-Output "    Custom Attributes:"
        $workspace.'Custom Attributes' | Format-List
    }
}

Write-Log "Workspace retrieval completed successfully."

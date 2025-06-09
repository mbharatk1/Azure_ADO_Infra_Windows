# Update a list of documents' metadata leveraging this endpoint: https://help.imanage.com/hc/en-us/articles/4412558535067-iManage-Work-Universal-API-Reference-Guide-REST-v2-#patch-/work/api/v2/customers/-customerId-/libraries/-libraryId-/documents/-docId-


# Force PowerShell to use TLS 1.2 instead of default TLS 1.0
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Set the Content-Type to application/x-www-form-urlencoded
$header = @{
    "Accept" = "*/*";
    "Content-Type" = "application/x-www-form-urlencoded"
}
write-host '-------LOGIN INFORMATION-------

'
# For URLs like 'imanage.work' use the format 'xxxxx-mobility.imanage.work'.
# For URLs like 'cloudimanage.com use 'cloudimanage.com' or the vanity code variant specified in Control Center.
$server = 'xxxxx-mobility.imanage.work'

# Store the library ID in a variable.
$library =  'xxxxx'

# Store the input variables for signing in.
# For URLs like 'imanage.work', the account must be virutal and in the NRTADMIN group. Use the 'User ID' found in Control Center.
# For URLs like 'cloudimanage.com', the account must be virtual and in the NRTADMIN group. Use the 'email' found in Control Center.
$username =  'xxxxx'
$securedValue = Read-Host -Prompt 'Password' -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securedValue)
$password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
# For URLs like 'imanage.work', the client id and secret can be found in the associated Control Center application.
# For URLs like 'cloudimanage.com' reach out to iManage Support to recieve your client id and secret.
$client_id =  'xxxxx'
$client_secret =  'xxxxx'


# Enter metadata field to be updated. Examples:
# author
# name
# description
# custom1
# custom3
$metadata1 =  'xxxxx'

# If updating only one metadata field, leave this parameter empty. If updating two, enter second metadata to be updated. Examples:
# custom2
$metadata2 =  ''

# Full path for the CSV data file of documents and metadata values. If updating one metadata field the format of the data file will DocumentID,metadata_value1. If updating two metadata fields, the format will be DocumentID,metadata_value1,metadata_value2.
$datafile =  'C:\xxxx\yyyy\datafile.csv'

function SignIn() {
    try {
        # Create object which is used as a payload to pass the user ID and password.
        # Requires Work Server 10.2.2 and later.
        $parameters = @{
            "username"  = $username;
            "password" = $password;
            "grant_type" = "password";
            "client_id" = $client_id;
            "client_secret" = $client_secret;
            "scope" = "admin";
        }

        # Send the 'POST' request to the server and store the response in a variable.
        $response = Invoke-RestMethod -Method Post -Uri "https://$server/auth/oauth2/token" -Header $header -Body $parameters

        # Retrieve the authorization token if present.
        # This token is required to be passed in future API requests.
        $x_auth_token = $response.$("access_token")

        return $x_auth_token
    }
    catch {
        Write-Host -Message "Sign in unsuccessful, exiting"

        if ($_.Exception.Response)
        {
            # HTTP error response (server response)
            Write-Host -Message "$($_.Exception.Response.StatusCode.value__)- $($_.Exception.Response.StatusDescription)"
        }
        else
        {
            # Other exceptions (e.g., unable to locate remote server)
            Write-Host -Message "$($_.ToString())"
        }

        exit
    }
}

function SignOut() {
    try {
        $response = Invoke-RestMethod -Method Get -Uri "https://$server/login/terminate" -Header $header
        Write-Host -Message "Sign out successful"
    }
    catch {
        Write-Host -Message "Sign out unsuccessful, exiting"

        if ($_.Exception.Response)
        {
            # HTTP error response (server response)
            Write-Host -Message "$($_.Exception.Response.StatusCode.value__)- $($_.Exception.Response.StatusDescription)"
        }
        else
        {
            # Other exceptions (e.g., unable to locate remote server)
            Write-Host -Message "$($_.ToString())"
        }

        exit
    }
}

function GetCustomerID() {
    try {
        $response = Invoke-RestMethod -Method Get -Uri "https://$server/api" -Header $header
        $customerId = $response.data.user.customer_id

        return $customerId
    }
    catch {
        Write-Host -Message "API call unsuccessful, exiting"

        if ($_.Exception.Response)
        {
            # HTTP error response (server response)
            Write-Host -Message "$($_.Exception.Response.StatusCode.value__)- $($_.Exception.Response.StatusDescription)"
        }
        else
        {
            # Other exceptions (e.g., unable to locate remote server)
            Write-Host -Message "$($_.ToString())"
        }

        exit
    }
}

function Main() {
    $XAuthToken = SignIn
    $header["X-Auth-Token"] = $XAuthToken
    $header["Content-Type"] = "application/json"
    $customer_id = GetCustomerID
	
	Get-Content $datafile
	$confirm = Read-Host -Prompt '
---------------------------------------------
You are about to update the above documents. 
If you want to proceed, enter Y. 
If you do not want to proceed, enter N.
---------------------------------------------
'
	
	if ($confirm -eq "Y")
	{

    Import-CSV $datafile -Header "id", "data1", "data2" | ForEach-Object {
    if ($metadata2){
	    # Set the metadata values for the WS being updated.
        $payload_class = @{
		$metadata1 = $_.data1;
        $metadata2 = $_.data2;
		}}
    else {
	    # Set the metadata values for the WS being updated.
        $payload_class = @{
		$metadata1 = $_.data1;
        #$metadata2 = $_.data2;
		}}

		
		write-host $payload_class.profile
		
		try {
		    # Send the request as an HTTP 'PATCH' request.
		    $response = Invoke-RestMethod -Method Patch -Uri "https://$server/api/v2/customers/$customer_id/libraries/$library/documents/$($_.id)" -Header $header -Body ($payload_class|ConvertTo-Json)
		    Write-Host -Message "Successfully updated WS ($($_.id))"
		}
		catch {
            Write-Host -Message "WS update failed. ($($_.id))"

            if ($_.Exception.Response)
            {
                # HTTP error response (server response)
                Write-Host -Message "$($_.Exception.Response.StatusCode.value__)- $($_.Exception.Response.StatusDescription)"
            }
            else
            {
                # Other exceptions (e.g., unable to locate remote server)
                Write-Host -Message "$($response.error.code_message)"
            }
		}
	}
	}

    SignOut
		Read-Host -Prompt "
-------------------
Press Enter to exit
-------------------
	"
}

Main

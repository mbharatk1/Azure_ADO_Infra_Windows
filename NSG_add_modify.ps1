# === CONFIGURATION ===
$resourceGroup     = "myResourceGroup"
$nsgName           = "myNSG"
$ruleName          = "Allow-HTTP-Inbound"
$priority          = 300
$direction         = "Inbound"
$access            = "Allow"
$protocol          = "Tcp"
$sourcePortRange   = "*"
$destinationPort   = "80"
$sourceAddress     = "*"
$destinationAddress = "*"

# === Connect to Azure (if needed) ===
# Connect-AzAccount

# === Fetch the NSG ===
$nsg = Get-AzNetworkSecurityGroup -Name $nsgName -ResourceGroupName $resourceGroup

# === Check for an existing rule ===
$existingRule = $nsg.SecurityRules | Where-Object { $_.Name -eq $ruleName }

if ($existingRule) {
    Write-Host "🔁 Rule '$ruleName' already exists. Updating..."

    # Update the properties of the existing rule
    $existingRule.Description              = "Updated rule to allow HTTP"
    $existingRule.Access                   = $access
    $existingRule.Protocol                 = $protocol
    $existingRule.Direction                = $direction
    $existingRule.Priority                 = $priority
    $existingRule.SourceAddressPrefix      = $sourceAddress
    $existingRule.SourcePortRange          = $sourcePortRange
    $existingRule.DestinationAddressPrefix = $destinationAddress
    $existingRule.DestinationPortRange     = $destinationPort
} else {
    Write-Host "➕ Rule '$ruleName' not found. Creating new rule..."

    # Create a new security rule
    $newRule = New-AzNetworkSecurityRuleConfig `
        -Name $ruleName `
        -Description "Allow inbound HTTP traffic" `
        -Access $access `
        -Protocol $protocol `
        -Direction $direction `
        -Priority $priority `
        -SourceAddressPrefix $sourceAddress `
        -SourcePortRange $sourcePortRange `
        -DestinationAddressPrefix $destinationAddress `
        -DestinationPortRange $destinationPort

    $nsg.SecurityRules.Add($newRule)
}

# === Apply the updated NSG ===
Set-AzNetworkSecurityGroup -NetworkSecurityGroup $nsg

Write-Host "✅ NSG rule '$ruleName' processed successfully."

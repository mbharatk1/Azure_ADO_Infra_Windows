========================================================================
Multiple rules
This version still adds or updates all three rules—AllowCustomInbound, rule2_ports_65001, and AllowAzureLoadBalancer
========================================================================


# NSG details
$ResourceGroupName = "myResourceGroup"
$NSGName = "myNSG"

# Define all rules with their individual source/destination IPs
$rules = @(
    @{
        Name = "AllowCustomInbound"
        Priority = 1000
        Ports = "8080,443"
        SourceAddresses = @("1.1.1.1", "1.1.1.2")
        DestinationAddresses = @("10.0.0.4")
        Protocol = "*"
        Description = "Allow 8080,443 from 1.1.1.1/1.1.1.2 to 10.0.0.4"
    },
    @{
        Name = "rule2_ports_65001"
        Priority = 1050
        Ports = "65001,65000"
        SourceAddresses = @("1.1.2.2", "1.1.2.3")
        DestinationAddresses = @("10.0.0.5")
        Protocol = "Tcp"
        Description = "Allow 65001,65000 from 1.1.2.2/1.1.2.3 to 10.0.0.5"
    },
    @{
        Name = "AllowAzureLoadBalancer"
        Priority = 1100
        Ports = "*"
        SourceAddresses = @("AzureLoadBalancer")
        DestinationAddresses = @("*")
        Protocol = "*"
        Description = "Allow Azure Load Balancer traffic"
    }
)

# Load NSG
try {
    $nsg = Get-AzNetworkSecurityGroup -ResourceGroupName $ResourceGroupName -Name $NSGName
    Write-Host "Loaded NSG: $NSGName"
}
catch {
    Write-Host "Error: Failed to load NSG '$NSGName' - $_"
    throw
}

# Process rules
foreach ($rule in $rules) {
    $existingRule = $nsg.SecurityRules | Where-Object { $_.Name -eq $rule.Name }

    if ($existingRule) {
        Write-Host "Updating rule: $($rule.Name)"
        $existingRule.SourceAddressPrefixes = $rule.SourceAddresses
        $existingRule.DestinationAddressPrefixes = $rule.DestinationAddresses
        $existingRule.DestinationPortRanges = $rule.Ports -split ","
        $existingRule.Access = "Allow"
        $existingRule.Direction = "Inbound"
        $existingRule.Priority = $rule.Priority
        $existingRule.Protocol = $rule.Protocol
        $existingRule.Description = $rule.Description

        try {
            Set-AzNetworkSecurityRuleConfig -NetworkSecurityGroup $nsg -SecurityRule $existingRule
            Write-Host "Updated rule: $($rule.Name)"
        }
        catch {
            Write-Host "Error updating rule '$($rule.Name)' - $_"
            throw
        }
    }
    else {
        Write-Host "Creating rule: $($rule.Name)"
        try {
            $newRule = New-AzNetworkSecurityRuleConfig `
                -Name $rule.Name `
                -Description $rule.Description `
                -Access Allow `
                -Protocol $rule.Protocol `
                -Direction Inbound `
                -Priority $rule.Priority `
                -SourceAddressPrefixes $rule.SourceAddresses `
                -SourcePortRange "*" `
                -DestinationAddressPrefixes $rule.DestinationAddresses `
                -DestinationPortRanges ($rule.Ports -split ",")

            $nsg.SecurityRules.Add($newRule)
            Write-Host "Created rule: $($rule.Name)"
        }
        catch {
            Write-Host "Error creating rule '$($rule.Name)' - $_"
            throw
        }
    }
}

# Save NSG
try {
    Set-AzNetworkSecurityGroup -NetworkSecurityGroup $nsg
    Write-Host "All rules successfully applied to NSG: $NSGName"
}
catch {
    Write-Host "Error committing changes to NSG '$NSGName' - $_"
    throw
}

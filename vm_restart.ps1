# Get all VMs in the resource group
$vms = Get-AzVM -ResourceGroupName "myResourceGroup"

# Loop through each VM and restart it
foreach ($vm in $vms) {
    Write-Host "Restarting VM: $($vm.Name)"
    try {
        Restart-AzVM -ResourceGroupName "myResourceGroup" -Name $vm.Name -Force -NoWait
        Write-Host "$($vm.Name) restart initiated"
    }
    catch {
        Write-Host "Failed to restart $($vm.Name): $_"
    }
}

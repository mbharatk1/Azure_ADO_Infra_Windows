variables:
  diskName: 'your-disk-name'
  resourceGroup: 'your-resource-group'
  vmName: 'your-vm-name'
  newSize: 1024  # in GiB

steps:
- task: AzureCLI@2
  inputs:
    azureSubscription: 'your-service-connection'
    scriptType: 'ps'
    scriptLocation: 'inlineScript'
    inlineScript: |
      az disk update `
        --name $(diskName) `
        --resource-group $(resourceGroup) `
        --size-gb $(newSize)

      az vm run-command invoke `
        --command-id RunPowerShellScript `
        --name $(vmName) `
        --resource-group $(resourceGroup) `
        --scripts "Resize-Partition -DriveLetter D -Size $(newSize)GB"

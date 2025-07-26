$sw = [System.Diagnostics.Stopwatch]::StartNew()

Get-ChildItem -Path "C:\Your\Target\Directory" -Recurse -File | Select-Object -First 1000 | ForEach-Object {
    Get-FileHash -Path $_.FullName -Algorithm SHA256
}

$sw.Stop()
Write-Output "Time for 1000 files: $($sw.Elapsed.TotalSeconds) seconds"

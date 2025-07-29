$pattern = "abc def ghi k"
$lines = [System.IO.File]::ReadLines("C:\path\to\your\file.txt")
$last100 = $lines | Select-Object -Last 100
$last100 | Where-Object { $_ -match $pattern }

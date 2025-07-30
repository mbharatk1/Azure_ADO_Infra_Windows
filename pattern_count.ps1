$pattern = "abc def ghi k"
$counter = 0
foreach ($line in [System.IO.File]::ReadLines("C:\path\to\your\file.txt")) {
    if ($line -match $pattern) { $counter++ }
}
$counter

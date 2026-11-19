# Read-only environment audit for M001.3. Prints no environment variables,
# credentials, API keys or secrets. Does not modify the system.
Write-Output "=== CPU ==="
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | Format-List

Write-Output "=== RAM ==="
$os = Get-CimInstance Win32_OperatingSystem
"PhysicalGB=$([math]::Round($os.TotalVisibleMemorySize/1MB,2))"
$a = (Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory).AvailableMBytes
"AvailableGB=$([math]::Round($a/1024,2))"

Write-Output "=== OS ==="
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture | Format-List

Write-Output "=== GPU ==="
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, AdapterRAM | Format-List

Write-Output "=== DISK ==="
Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" | Select-Object @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,2)}} | Format-List

Write-Output "=== WSL ==="
wsl.exe --status 2>&1
wsl.exe --list --verbose 2>&1

Write-Output "=== DOCKER ==="
docker.exe version 2>&1
docker.exe compose version 2>&1

Write-Output "=== PORT 8080 ==="
$c = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($c) { $c | Select-Object LocalAddress, LocalPort, State | Format-Table -AutoSize } else { "No listener on 8080" }

Write-Output "=== PYTHON / OLLAMA ==="
python --version 2>&1
$oll = Get-Command ollama -ErrorAction SilentlyContinue
if ($oll) { ollama --version 2>&1; ollama list 2>&1 } else { "ollama not found" }

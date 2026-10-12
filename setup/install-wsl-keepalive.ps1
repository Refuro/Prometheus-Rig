# Run once in PowerShell as Administrator:
#   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\OneDrive\Documents\Projects\OpenRig\setup\install-wsl-keepalive.ps1"
# Starts Ubuntu invisibly at every Windows sign-in and keeps it running, so
# agents and the logger survive closing all terminal windows.
$name = "WSL keep-alive (OpenRig)"
$action = New-ScheduledTaskAction -Execute "conhost.exe" -Argument "--headless wsl.exe -d Ubuntu-24.04 --exec sleep infinity"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $name
Write-Host "Installed and started: $name"
Write-Host "Remove later with: Unregister-ScheduledTask -TaskName '$name' -Confirm:`$false"

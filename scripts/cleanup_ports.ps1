# Kill processes on specific ports
$ports = @(8001, 5173)

foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($process) {
        $pid_val = $process.OwningProcess
        Write-Host "Killing process $pid_val on port $port"
        Stop-Process -Id $pid_val -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "No process found on port $port"
    }
}
Write-Host "Cleanup complete."

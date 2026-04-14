$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$projectRoot = Split-Path -Parent $PSScriptRoot
$gitRoot = $null
try {
    $gitRoot = (& git -C $projectRoot rev-parse --show-toplevel 2>$null)
} catch {
    $gitRoot = $null
}

Write-Host "==============================================="
Write-Host "Burlan Project Scope Check"
Write-Host "==============================================="
Write-Host ("Project root: " + $projectRoot)
if ($gitRoot) {
    Write-Host ("Git root: " + $gitRoot)
}
Write-Host ""

Write-Host "[1] Project checks"
& python (Join-Path $projectRoot "scripts\check_runtime_boundary.py")
& python (Join-Path $projectRoot "scripts\check_text_encoding.py")
& python (Join-Path $projectRoot "scripts\scan_legacy_terms.py")
Write-Host ""

Write-Host "[2] Git status for this project only"
& git -C $projectRoot status --short -- .

# PowerShell script to install core tools

$ErrorActionPreference = "Stop"

# Function to locate uv.exe
function Find-Uv {
    $cmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    
    # Check common paths
    $paths = @(
        "$env:USERPROFILE\.local\bin\uv.exe",
        "$env:LOCALAPPDATA\Microsoft\WinGet\Links\uv.exe",
        "$env:APPDATA\Local\Microsoft\WinGet\Links\uv.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) {
            return $p
        }
    }
    return $null
}

Write-Host "Step 1: Checking for uv..."
$uvPath = Find-Uv

if (-not $uvPath) {
    Write-Host "uv not found. Installing astral-sh.uv via WinGet..."
    try {
        # Try WinGet first as requested by guide
        Start-Process winget -ArgumentList "install --id astral-sh.uv --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -Wait
        Start-Sleep -Seconds 5
        $uvPath = Find-Uv
    } catch {
        Write-Host "WinGet installation failed or timed out. Trying official installer fallback..."
    }
    
    if (-not $uvPath) {
        # Fallback to official script
        Write-Host "Installing uv via official installer script..."
        powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
        Start-Sleep -Seconds 3
        $uvPath = Find-Uv
    }
}

if (-not $uvPath) {
    Write-Error "Failed to install/find uv. Please install it manually or check internet connection."
}

Write-Host "Using uv from: $uvPath"

Write-Host "Step 2: Creating virtual environment .venv with Python 3.12..."
# Create venv with python 3.12 (uv will fetch it if not present)
& $uvPath venv --python 3.12

Write-Host "Step 3: Installing core packages from requirements-core.txt..."
# Install requirements
& $uvPath pip install -r requirements-core.txt

Write-Host "Step 4: Running verify_core.py..."
# Verify installation
if (Test-Path ".\.venv\Scripts\python.exe") {
    & ".\.venv\Scripts\python.exe" verify_core.py
} else {
    Write-Error "Virtual environment python.exe not found at .\.venv\Scripts\python.exe"
}

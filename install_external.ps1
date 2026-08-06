# PowerShell script to install external tools and register MCP servers

$ErrorActionPreference = "Stop"

# 1. Install GitHub CLI via winget
Write-Host "Step 1: Installing GitHub CLI (gh)..."
$ghCmd = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghCmd) {
    Write-Host "GitHub CLI not found. Installing via winget..."
    try {
        Start-Process winget -ArgumentList "install --id GitHub.cli --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -Wait
        Write-Host "GitHub CLI installation command executed."
    } catch {
        Write-Host "Winget installation of gh failed: $_"
    }
} else {
    Write-Host "GitHub CLI is already installed at: $($ghCmd.Source)"
}

# 2. Install Firebase CLI globally via npm
Write-Host "`nStep 2: Installing Firebase CLI (firebase-tools)..."
Write-Host "Installing firebase-tools globally..."
try {
    Start-Process npm.cmd -ArgumentList "install -g firebase-tools" -NoNewWindow -Wait
    Write-Host "Firebase tools installed."
} catch {
    Write-Host "Failed to install firebase-tools: $_"
}

# 3. Install Obsidian MCP globally via npm
Write-Host "`nStep 3: Installing Obsidian MCP (mcpvault)..."
Write-Host "Installing @bitbonsai/mcpvault globally..."
try {
    Start-Process npm.cmd -ArgumentList "install -g @bitbonsai/mcpvault" -NoNewWindow -Wait
    Write-Host "mcpvault installed."
} catch {
    Write-Host "Failed to install @bitbonsai/mcpvault: $_"
}

# 4. Update mcp_config.json
Write-Host "`nStep 4: Registering MCP servers in mcp_config.json..."
$pythonCmd = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonCmd)) {
    $pythonCmd = "python"
}

$updateScript = @'
import json, os
p = r"C:\Users\H-04137\.gemini\config\mcp_config.json"
if os.path.exists(p):
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {}

if "mcpServers" not in data:
    data["mcpServers"] = {}

# Add notebooklm
data["mcpServers"]["notebooklm"] = {
    "command": "nlm",
    "args": ["mcp"]
}

# Add obsidian
appdata = os.environ.get("APPDATA", "")
mcpvault_path = os.path.join(appdata, "npm", "mcpvault.cmd")
vault_path = r"C:\Users\H-04137\.gemini\antigravity\scratch\SecondBrain_Local"
data["mcpServers"]["obsidian"] = {
    "command": mcpvault_path,
    "args": [vault_path]
}

# Add firebase
data["mcpServers"]["firebase"] = {
    "command": "npx.cmd",
    "args": ["-y", "firebase-tools@latest", "mcp"]
}

with open(p, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Successfully updated mcp_config.json!")
'@

& $pythonCmd -c $updateScript

# 5. Make sure npm global path is in user path
Write-Host "`nStep 5: Updating PATH for current session and user..."
$npmPath = Join-Path $env:APPDATA "npm"
if (Test-Path $npmPath) {
    if ($env:PATH -notlike "*$npmPath*") {
        $env:PATH += ";$npmPath"
        Write-Host "Added $npmPath to session PATH."
        [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$npmPath", "User")
    } else {
        Write-Host "npm global path already in PATH."
    }
}

Write-Host "`nInstallation and MCP registration completed."

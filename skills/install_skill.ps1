<#
.SYNOPSIS
    One-click installer for the youtube-kb-builder skill into Google Antigravity, Claude Code, and Codex.
.DESCRIPTION
    Copies the youtube-kb-builder skill directory into the target agent configuration folders.
#>

[CmdletBinding()]
param (
    [switch]$AllAgents
)

$ErrorActionPreference = "Stop"

$sourcePath = Join-Path $PSScriptRoot "youtube-kb-builder"

if (-not (Test-Path $sourcePath)) {
    Write-Error "Skill source not found at: $sourcePath"
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Installing youtube-kb-builder Skill to Global Agent Config" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Target: Google Antigravity / Gemini CLI
$targetGemini = Join-Path $HOME ".gemini\config\skills\youtube-kb-builder"
# Check if D:\.gemini junction exists
if (Test-Path "D:\.gemini\config\skills") {
    $targetGemini = "D:\.gemini\config\skills\youtube-kb-builder"
}

Write-Host "`n[1/3] Installing to Google Antigravity ($targetGemini)..." -ForegroundColor Yellow
if (-not (Test-Path (Split-Path $targetGemini))) {
    New-Item -ItemType Directory -Path (Split-Path $targetGemini) -Force | Out-Null
}
Copy-Item -Path $sourcePath -Destination (Split-Path $targetGemini) -Recurse -Force
Write-Host " -> Installed successfully for Google Antigravity!" -ForegroundColor Green

# 2. Target: Claude Code (if enabled or present)
$targetClaude = Join-Path $HOME ".claude\skills\youtube-kb-builder"
if ($AllAgents -or (Test-Path (Join-Path $HOME ".claude"))) {
    Write-Host "`n[2/3] Installing to Claude Code ($targetClaude)..." -ForegroundColor Yellow
    if (-not (Test-Path (Split-Path $targetClaude))) {
        New-Item -ItemType Directory -Path (Split-Path $targetClaude) -Force | Out-Null
    }
    Copy-Item -Path $sourcePath -Destination (Split-Path $targetClaude) -Recurse -Force
    Write-Host " -> Installed successfully for Claude Code!" -ForegroundColor Green
} else {
    Write-Host "`n[2/3] Skipping Claude Code (directory not found, use -AllAgents to force install)" -ForegroundColor Gray
}

# 3. Target: OpenAI Codex / Cursor agents
$targetCodex = Join-Path $HOME ".agents\skills\youtube-kb-builder"
if ($AllAgents -or (Test-Path (Join-Path $HOME ".agents"))) {
    Write-Host "`n[3/3] Installing to Codex / Agent Directory ($targetCodex)..." -ForegroundColor Yellow
    if (-not (Test-Path (Split-Path $targetCodex))) {
        New-Item -ItemType Directory -Path (Split-Path $targetCodex) -Force | Out-Null
    }
    Copy-Item -Path $sourcePath -Destination (Split-Path $targetCodex) -Recurse -Force
    Write-Host " -> Installed successfully for Codex!" -ForegroundColor Green
} else {
    Write-Host "`n[3/3] Skipping Codex (directory not found, use -AllAgents to force install)" -ForegroundColor Gray
}

Write-Host "`n[SUCCESS] youtube-kb-builder skill is now installed and ready to use across your AI agents!" -ForegroundColor Green

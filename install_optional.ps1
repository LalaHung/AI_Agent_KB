# PowerShell script to install optional packages and system tools for Windows

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

# 1. Find uv
Write-Host "Checking for uv..."
$uvPath = Find-Uv
if (-not $uvPath) {
    Write-Error "uv not found. Please install uv first using install_windows.ps1."
}
Write-Host "Using uv from: $uvPath"

# 2. Install optional Python packages
Write-Host "`nStep 1: Installing optional Python packages..."
$optionalPackages = @(
    "docxcompose",
    "xlsxwriter",
    "pandas",
    "pdfplumber",
    "pdf2image",
    "fpdf2",
    "ocrmypdf",
    "docx2pdf",
    "pywin32",
    "edge-tts",
    "yt-dlp",
    "youtube-transcript-api"
)

foreach ($pkg in $optionalPackages) {
    Write-Host "Installing $pkg..."
    & $uvPath pip install $pkg
}

# 3. Install Tesseract OCR via Winget
Write-Host "`nStep 2: Installing Tesseract OCR..."
$tesseractCmd = Get-Command tesseract -ErrorAction SilentlyContinue
if (-not $tesseractCmd) {
    Write-Host "Tesseract not found. Installing via winget..."
    try {
        Start-Process winget -ArgumentList "install --id tesseract-ocr.tesseract --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -Wait
        Write-Host "Tesseract installation command executed."
    } catch {
        Write-Host "Winget installation of Tesseract failed: $_"
    }
} else {
    Write-Host "Tesseract is already installed at: $($tesseractCmd.Source)"
}

# 4. Install Poppler via Winget
Write-Host "`nStep 3: Installing Poppler..."
$popplerCmd = Get-Command pdftoppm -ErrorAction SilentlyContinue
if (-not $popplerCmd) {
    Write-Host "Poppler (pdftoppm) not found. Installing via winget..."
    try {
        Start-Process winget -ArgumentList "install --id oschwartz10612.Poppler --silent --accept-source-agreements --accept-package-agreements" -NoNewWindow -Wait
        Write-Host "Poppler installation command executed."
    } catch {
        Write-Host "Winget installation of Poppler failed: $_"
    }
} else {
    Write-Host "Poppler (pdftoppm) is already installed at: $($popplerCmd.Source)"
}

# 5. Install Ghostscript via Direct Download
Write-Host "`nStep 4: Installing Ghostscript..."
$gsCmd = Get-Command gswin64c -ErrorAction SilentlyContinue
if (-not $gsCmd) {
    Write-Host "Ghostscript (gswin64c) not found."
    
    # Define installer details
    $gsUrl = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10071/gs10071w64.exe"
    $tempInstaller = Join-Path $env:TEMP "gs10071w64.exe"
    
    Write-Host "Downloading Ghostscript from $gsUrl..."
    try {
        Invoke-WebRequest -Uri $gsUrl -OutFile $tempInstaller -UseBasicParsing
        Write-Host "Downloaded to $tempInstaller. Installing silently..."
        # Run installer with /S switch silently and Verb RunAs (Admin elevation)
        $proc = Start-Process -FilePath $tempInstaller -ArgumentList "/S" -Verb RunAs -Wait -PassThru
        if ($proc.ExitCode -ne 0) {
            Write-Host "Warning: Ghostscript installation exited with code $($proc.ExitCode)"
        } else {
            Write-Host "Ghostscript installed successfully."
        }
    } catch {
        Write-Host "Failed to download or install Ghostscript: $_"
    } finally {
        if (Test-Path $tempInstaller) {
            Remove-Item $tempInstaller -Force
        }
    }
} else {
    Write-Host "Ghostscript is already installed at: $($gsCmd.Source)"
}

# 6. Add directories to Path if needed
Write-Host "`nStep 5: Updating PATH for current session..."

# Find Tesseract directory
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR",
    "C:\Program Files (x86)\Tesseract-OCR",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR"
)
$foundTesseract = $null
foreach ($tp in $tesseractPaths) {
    if (Test-Path (Join-Path $tp "tesseract.exe")) {
        $foundTesseract = $tp
        break
    }
}
if ($foundTesseract) {
    Write-Host "Found Tesseract directory: $foundTesseract"
    if ($env:PATH -notlike "*$foundTesseract*") {
        $env:PATH += ";$foundTesseract"
        Write-Host "Added Tesseract directory to session PATH."
        # Update user environment PATH permanently
        [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$foundTesseract", "User")
    }
}

# Find Ghostscript directory
$gsRoot = "C:\Program Files\gs"
if (Test-Path $gsRoot) {
    $gsDirs = Get-ChildItem -Path $gsRoot -Directory -ErrorAction SilentlyContinue
    $foundGsBin = $null
    foreach ($gd in $gsDirs) {
        $binPath = Join-Path $gd.FullName "bin"
        if (Test-Path (Join-Path $binPath "gswin64c.exe")) {
            $foundGsBin = $binPath
            break
        }
    }
    if ($foundGsBin) {
        Write-Host "Found Ghostscript bin directory: $foundGsBin"
        if ($env:PATH -notlike "*$foundGsBin*") {
            $env:PATH += ";$foundGsBin"
            Write-Host "Added Ghostscript bin directory to session PATH."
            # Update user environment PATH permanently
            [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$foundGsBin", "User")
        }
    }
}

# Find Poppler directory
$popplerLinks = "$env:LOCALAPPDATA\Microsoft\WinGet\Links"
if (Test-Path (Join-Path $popplerLinks "pdftoppm.exe")) {
    Write-Host "Found Poppler in WinGet Links directory: $popplerLinks"
    if ($env:PATH -notlike "*$popplerLinks*") {
        $env:PATH += ";$popplerLinks"
        Write-Host "Added WinGet Links to session PATH."
    }
} else {
    # Check if extracted elsewhere
    $packagesRoot = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages"
    if (Test-Path $packagesRoot) {
        $popplerDirs = Get-ChildItem -Path $packagesRoot -Filter "*Poppler*" -Directory -Recurse -ErrorAction SilentlyContinue
        foreach ($pd in $popplerDirs) {
            $binPath = Join-Path $pd.FullName "Library\bin"
            if (-not (Test-Path $binPath)) {
                # sometimes it might be just bin or directly in folder
                $binPath = $pd.FullName
            }
            if (Test-Path (Join-Path $binPath "pdftoppm.exe")) {
                Write-Host "Found Poppler bin directory: $binPath"
                if ($env:PATH -notlike "*$binPath*") {
                    $env:PATH += ";$binPath"
                    Write-Host "Added Poppler directory to session PATH."
                    [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$binPath", "User")
                }
                break
            }
        }
    }
}

Write-Host "`nInstallation completed."

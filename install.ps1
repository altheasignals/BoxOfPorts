# ejoinctl Installation Script for Windows
# Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.
#
# PowerShell installation script for ejoinctl on Windows

param(
    [switch]$SkipDeps,
    [switch]$Force,
    [switch]$Help
)

# Project information
$PROJECT_NAME = "ejoinctl"
$VERSION = "1.0.0"
$AUTHOR = "Althea Signals Network LLC"
$MIN_PYTHON_VERSION = [Version]"3.11.0"

# Functions
function Write-Log {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}

function Show-Banner {
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host "  ejoinctl v$VERSION - EJOIN Gateway Management CLI" -ForegroundColor Blue
    Write-Host "  Developed by $AUTHOR" -ForegroundColor Blue
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host ""
}

function Show-Help {
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipDeps     Skip system dependency installation"
    Write-Host "  -Force        Force installation even if already installed"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1"
    Write-Host "  .\install.ps1 -Force"
    Write-Host "  .\install.ps1 -SkipDeps"
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-Python {
    Write-Log "Checking Python installation..."
    
    $pythonCmd = $null
    
    # Check for python3 command
    try {
        $python3Version = python3 --version 2>$null
        if ($python3Version) {
            $pythonCmd = "python3"
        }
    } catch {}
    
    # Check for python command
    if (-not $pythonCmd) {
        try {
            $pythonVersion = python --version 2>$null
            if ($pythonVersion) {
                $pythonCmd = "python"
            }
        } catch {}
    }
    
    if (-not $pythonCmd) {
        Write-Error "Python is not installed. Please install Python $MIN_PYTHON_VERSION+ from https://www.python.org/downloads/windows/"
    }
    
    # Get version
    $versionOutput = & $pythonCmd --version
    $versionString = $versionOutput -replace "Python ", ""
    $currentVersion = [Version]$versionString
    
    Write-Log "Found Python $currentVersion"
    
    if ($currentVersion -lt $MIN_PYTHON_VERSION) {
        Write-Error "Python $MIN_PYTHON_VERSION+ required. Found: $currentVersion"
    }
    
    Write-Log "✓ Python version check passed"
    return $pythonCmd
}

function Test-Pip {
    param([string]$PythonCmd)
    
    Write-Log "Checking pip installation..."
    
    try {
        $pipVersion = & $PythonCmd -m pip --version
        Write-Log "✓ Found pip: $pipVersion"
        return "$PythonCmd -m pip"
    } catch {
        Write-Error "pip is not installed. Please install pip first."
    }
}

function Install-SystemDependencies {
    if ($SkipDeps) {
        Write-Log "Skipping system dependencies installation"
        return
    }
    
    Write-Log "Checking system dependencies..."
    
    # Check for Chocolatey (optional)
    try {
        $chocoVersion = choco --version 2>$null
        if ($chocoVersion) {
            Write-Log "Found Chocolatey: $chocoVersion"
            
            # Install Git if not present
            if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
                Write-Log "Installing Git via Chocolatey..."
                choco install git -y
            }
        }
    } catch {
        Write-Warning "Chocolatey not found. Some features may require additional setup."
    }
    
    Write-Log "✓ System dependencies check complete"
}

function New-VirtualEnvironment {
    param([string]$PythonCmd)
    
    Write-Log "Creating virtual environment..."
    
    $venvDir = "$env:USERPROFILE\.ejoinctl\venv"
    $parentDir = Split-Path $venvDir -Parent
    
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
    
    & $PythonCmd -m venv $venvDir
    
    # Activate virtual environment
    $activateScript = "$venvDir\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    } else {
        Write-Error "Failed to create virtual environment"
    }
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    Write-Log "✓ Virtual environment created at $venvDir"
    return $venvDir
}

function Install-Ejoinctl {
    Write-Log "Installing ejoinctl..."
    
    # Check if we're in the source directory
    if ((Test-Path "pyproject.toml") -and (Get-Content "pyproject.toml" | Select-String -Pattern "ejoinctl")) {
        Write-Log "Installing from local source..."
        python -m pip install -e .
    } else {
        Write-Error "Please run this script from the ejoinctl source directory"
    }
    
    Write-Log "✓ ejoinctl installation complete"
}

function New-WrapperScript {
    param([string]$VenvDir)
    
    Write-Log "Creating wrapper script..."
    
    $wrapperDir = "$env:USERPROFILE\.local\bin"
    if (-not (Test-Path $wrapperDir)) {
        New-Item -ItemType Directory -Path $wrapperDir -Force | Out-Null
    }
    
    $wrapperScript = "$wrapperDir\ejoinctl.bat"
    
    $batchContent = @"
@echo off
call "$VenvDir\Scripts\activate.bat"
python -m ejoinctl.cli %*
"@
    
    Set-Content -Path $wrapperScript -Value $batchContent
    
    Write-Log "✓ Wrapper script created at $wrapperScript"
    return $wrapperDir
}

function Update-Path {
    param([string]$NewPath)
    
    Write-Log "Updating PATH environment variable..."
    
    # Get current user PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    # Check if path is already included
    if ($currentPath -split ";" | Where-Object { $_ -eq $NewPath }) {
        Write-Log "PATH already includes $NewPath"
        return
    }
    
    # Add to PATH
    $newPathValue = if ($currentPath) { "$currentPath;$NewPath" } else { $NewPath }
    [Environment]::SetEnvironmentVariable("PATH", $newPathValue, "User")
    
    # Update current session PATH
    $env:PATH = "$env:PATH;$NewPath"
    
    Write-Log "✓ Updated PATH environment variable"
}

function New-ConfigDirectory {
    Write-Log "Creating configuration directory..."
    
    $configDir = "$env:USERPROFILE\.config\ejoinctl"
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    # Copy example configuration if available
    if (Test-Path "server_access.csv") {
        Copy-Item "server_access.csv" "$configDir\gateways.csv.example"
        Write-Log "✓ Example gateway configuration copied"
    }
    
    Write-Log "✓ Configuration directory created at $configDir"
}

function Test-Installation {
    Write-Log "Testing installation..."
    
    try {
        $helpOutput = ejoinctl --help 2>$null
        if ($helpOutput) {
            Write-Log "✓ ejoinctl is working correctly"
        } else {
            Write-Warning "ejoinctl command not found. You may need to restart your PowerShell session."
        }
    } catch {
        Write-Warning "ejoinctl command not found. You may need to restart your PowerShell session."
        Write-Log "Try running: refreshenv (if using Chocolatey) or restart PowerShell"
    }
}

function Show-Completion {
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  Installation Complete!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "ejoinctl has been successfully installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick start commands:"
    Write-Host "  ejoinctl --help                 - Show help"
    Write-Host "  ejoinctl test-connection        - Test gateway connection"
    Write-Host ""
    Write-Host "Configuration:"
    Write-Host "  Config directory: $env:USERPROFILE\.config\ejoinctl"
    Write-Host "  Virtual environment: $env:USERPROFILE\.ejoinctl\venv"
    Write-Host ""
    Write-Host "Documentation:"
    Write-Host "  README.md - Main documentation"
    Write-Host "  DEPLOYMENT.md - Deployment guide"
    Write-Host "  USAGE_GUIDE.md - Complete usage examples"
    Write-Host ""
    Write-Host "Support: support@altheamesh.com"
    Write-Host "Website: https://altheamesh.com"
    Write-Host ""
    
    if (-not (Get-Command ejoinctl -ErrorAction SilentlyContinue)) {
        Write-Host "Note: Restart your PowerShell session to use ejoinctl" -ForegroundColor Yellow
    }
}

# Main installation function
function Main {
    if ($Help) {
        Show-Help
        exit 0
    }
    
    Show-Banner
    
    # Check if already installed
    if ((Get-Command ejoinctl -ErrorAction SilentlyContinue) -and (-not $Force)) {
        Write-Warning "ejoinctl is already installed. Use -Force to reinstall."
        ejoinctl --help
        exit 0
    }
    
    # Check execution policy
    $executionPolicy = Get-ExecutionPolicy
    if ($executionPolicy -eq "Restricted") {
        Write-Warning "PowerShell execution policy is Restricted. You may need to change it."
        Write-Host "Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        
        $response = Read-Host "Change execution policy now? (y/N)"
        if ($response -match "^[Yy]$") {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        }
    }
    
    # Installation steps
    $pythonCmd = Test-Python
    $pipCmd = Test-Pip $pythonCmd
    Install-SystemDependencies
    $venvDir = New-VirtualEnvironment $pythonCmd
    Install-Ejoinctl
    $wrapperDir = New-WrapperScript $venvDir
    Update-Path $wrapperDir
    New-ConfigDirectory
    Test-Installation
    Show-Completion
}

# Run main function
try {
    Main
} catch {
    Write-Error "Installation failed: $_"
    exit 1
}
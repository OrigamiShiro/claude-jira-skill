# Jira CLI Skill — one-line installer for Windows PowerShell.
#
# Usage:
#   iwr -useb https://raw.githubusercontent.com/OrigamiShiro/claude-jira-skill/main/bootstrap.ps1 | iex

$ErrorActionPreference = 'Stop'

$RepoUrl = if ($env:REPO_URL) { $env:REPO_URL } else { 'https://github.com/OrigamiShiro/claude-jira-skill' }
$Branch  = if ($env:BRANCH)   { $env:BRANCH }   else { 'main' }
$Dest    = if ($env:DEST)     { $env:DEST }     else { Join-Path $env:USERPROFILE '.claude\skills\jira' }

Write-Host "Jira CLI Skill — installer"
Write-Host "  repo: $RepoUrl"
Write-Host "  dest: $Dest"
Write-Host ""

if (Test-Path $Dest) {
    Write-Host "⚠ Destination already exists: $Dest"
    Write-Host "  Delete it first if you want a clean install:"
    Write-Host "  Remove-Item -Recurse -Force `"$Dest`""
    exit 1
}

$ParentDir = Split-Path $Dest -Parent
if (-not (Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "-> cloning via git"
    git clone --depth 1 -b $Branch $RepoUrl $Dest
} else {
    Write-Host "-> git not found - downloading zip"
    $TmpZip = Join-Path $env:TEMP "claude-jira-skill-$Branch.zip"
    $TmpDir = Join-Path $env:TEMP "claude-jira-skill-extract"

    if (Test-Path $TmpZip) { Remove-Item $TmpZip -Force }
    if (Test-Path $TmpDir) { Remove-Item $TmpDir -Recurse -Force }

    $ZipUrl = "$RepoUrl/archive/refs/heads/$Branch.zip"
    Invoke-WebRequest -Uri $ZipUrl -OutFile $TmpZip -UseBasicParsing
    Expand-Archive -Path $TmpZip -DestinationPath $TmpDir -Force

    $Extracted = Get-ChildItem $TmpDir | Select-Object -First 1
    Move-Item -Path $Extracted.FullName -Destination $Dest

    Remove-Item $TmpZip -Force
    Remove-Item $TmpDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
$PythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonExe) { $PythonExe = Get-Command py -ErrorAction SilentlyContinue }
if (-not $PythonExe) {
    Write-Host "ERROR: Python not found in PATH. Install Python 3.9+ from https://python.org"
    exit 1
}

& $PythonExe.Path (Join-Path $Dest 'install.py')

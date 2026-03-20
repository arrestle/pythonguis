<#
.SYNOPSIS
  Find the Windows "Scripts" folder for a Python install and add it to PATH.

.DESCRIPTION
  On Windows, pip/console_scripts install into <PythonRoot>\Scripts.
  This script resolves that folder from a chosen Python executable (default: `python` on PATH).

.PARAMETER Python
  Path to python.exe, or a command name (default: "python").

.PARAMETER Scope
  Session  - PATH change applies only to this PowerShell window (default).
  User     - Append to your user PATH permanently (open a new terminal after).

.EXAMPLE
  .\scripts\add-python-scripts-to-path.ps1

.EXAMPLE
  .\scripts\add-python-scripts-to-path.ps1 -Python py -PythonArgs @("-3.12") -Scope User
#>
[CmdletBinding()]
param(
    [string] $Python = "python",
    [string[]] $PythonArgs = @(),
    [ValidateSet("Session", "User")]
    [string] $Scope = "Session"
)

$ErrorActionPreference = "Stop"

function Get-PythonExecutable {
    param([string] $Cmd, [string[]] $PyArgs)
    if ($Cmd -match '[\\/]' -and (Test-Path -LiteralPath $Cmd)) {
        return (Resolve-Path -LiteralPath $Cmd).Path
    }
    $found = Get-Command $Cmd -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $found) {
        throw "Command not found: $Cmd"
    }
    if ($PyArgs.Count -gt 0) {
        $code = "import sys; print(sys.executable)"
        $out = & $found.Source @PyArgs -c $code 2>&1
        if (-not $out) {
            throw "Could not resolve interpreter for: $Cmd $($PyArgs -join ' ')"
        }
        return ($out | Select-Object -Last 1).ToString().Trim()
    }
    return $found.Source
}

$pyExe = Get-PythonExecutable -Cmd $Python -PyArgs $PythonArgs
$scriptsDir = Join-Path (Split-Path -Parent $pyExe) "Scripts"

if (-not (Test-Path -LiteralPath $scriptsDir)) {
    throw "Scripts folder does not exist: $scriptsDir"
}

Write-Host "Python:  $pyExe"
Write-Host "Scripts: $scriptsDir"

# pip --user puts console_scripts under PythonXY\Scripts, not getuserbase()\Scripts alone
$userScripts = (
    & $pyExe -c "import sysconfig, os; print(sysconfig.get_path('scripts', 'nt_user'))" 2>$null
).Trim()
$uvPrefix = Test-Path -LiteralPath (Join-Path $scriptsDir "uv.exe")
$uvUser = $userScripts -and (Test-Path -LiteralPath (Join-Path $userScripts "uv.exe"))
if (-not $uvPrefix -and $uvUser) {
    Write-Warning "uv.exe is under the user install (pip --user), not under prefix Scripts:`n  $userScripts`nAdd that folder to PATH, or install uv into prefix:`n  & '$pyExe' -m pip install -U uv"
} elseif (-not $uvPrefix -and -not $uvUser) {
    Write-Warning "uv.exe not found under $scriptsDir or user Scripts. Install with:`n  & '$pyExe' -m pip install -U uv`nThen re-run this script or use:  python -m uv ..."
}

function Add-ToSessionPath {
    param([string] $Dir)
    if (-not $Dir) { return }
    if ($env:Path -notlike "*$Dir*") {
        $env:Path = "$env:Path;$Dir"
        Write-Host "Appended to PATH for this session: $Dir"
    } else {
        Write-Host "Already on PATH for this session: $Dir"
    }
}

if ($Scope -eq "Session") {
    Add-ToSessionPath -Dir $scriptsDir
    if ($userScripts -and ($userScripts -ne $scriptsDir) -and (Test-Path -LiteralPath $userScripts)) {
        Add-ToSessionPath -Dir $userScripts
    }
    return
}

# User scope — append prefix Scripts and (if different) user Scripts
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$toAdd = @($scriptsDir) | ForEach-Object { $_ }
if ($userScripts -and ($userScripts -ne $scriptsDir) -and (Test-Path -LiteralPath $userScripts)) {
    $toAdd += $userScripts
}
$parts = if ($userPath) { $userPath.Split(';') } else { @() }
$changed = $false
foreach ($d in $toAdd) {
    if ($d -and ($parts -notcontains $d)) {
        $parts += $d
        $changed = $true
    }
}
if (-not $changed) {
    Write-Host "Both folders already present in user PATH (or nothing to add)."
    return
}
[Environment]::SetEnvironmentVariable("Path", ($parts -join ';'), "User")
Write-Host "Updated user PATH. Open a new terminal for it to take effect."

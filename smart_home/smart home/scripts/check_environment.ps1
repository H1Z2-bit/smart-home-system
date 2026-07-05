$ErrorActionPreference = "Continue"

function Show-Check {
    param (
        [string] $Name,
        [bool] $Ok,
        [string] $Detail = ""
    )

    $status = if ($Ok) { "[OK]" } else { "[MISSING]" }
    if ($Detail) {
        Write-Host "$status $Name - $Detail"
    } else {
        Write-Host "$status $Name"
    }
}

$cmake = Get-Command cmake -ErrorAction SilentlyContinue
if ($cmake) {
    $cmakeDetail = (& cmake --version)[0]
} else {
    $cmakeDetail = "Install CMake"
}
Show-Check "CMake" ($null -ne $cmake) $cmakeDetail

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    $gitDetail = & git --version
} else {
    $gitDetail = "Install Git"
}
Show-Check "Git" ($null -ne $git) $gitDetail

$vswhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
$vsPath = ""
if (Test-Path $vswhere) {
    $vsPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
}
if ($vsPath) {
    $vsDetail = $vsPath
} else {
    $vsDetail = "Install Desktop development with C++ in Visual Studio Installer"
}
Show-Check "MSVC C++ Build Tools" (-not [string]::IsNullOrWhiteSpace($vsPath)) $vsDetail

$vcpkgRoot = $env:VCPKG_ROOT
if ([string]::IsNullOrWhiteSpace($vcpkgRoot)) {
    if (Test-Path "C:\vcpkg\vcpkg.exe") {
        $vcpkgRoot = "C:\vcpkg"
    } elseif (Test-Path "D:\coding\vcpkg\vcpkg.exe") {
        $vcpkgRoot = "D:\coding\vcpkg"
    } else {
        $vcpkgRoot = "C:\vcpkg"
    }
}
$vcpkgExe = Join-Path $vcpkgRoot "vcpkg.exe"
$hasVcpkg = Test-Path $vcpkgExe
if ($hasVcpkg) {
    $vcpkgDetail = $vcpkgExe
} else {
    $vcpkgDetail = "Install vcpkg to C:\vcpkg and set VCPKG_ROOT"
}
Show-Check "vcpkg" $hasVcpkg $vcpkgDetail

$mysqlClient = Get-Command mysql -ErrorAction SilentlyContinue
if ($mysqlClient) {
    Show-Check "MySQL Client" $true (& mysql --version)
} else {
    $localMysql = "D:\coding\MySQL\bin\mysql.exe"
    $hasLocalMysql = Test-Path $localMysql
    if ($hasLocalMysql) {
        $mysqlDetail = & $localMysql --version
    } else {
        $mysqlDetail = "Install MySQL or add mysql.exe to PATH"
    }
    Show-Check "MySQL Client" $hasLocalMysql $mysqlDetail
}

$mysqlService = Get-Service MySQL -ErrorAction SilentlyContinue
if ($mysqlService) {
    $mysqlServiceDetail = "Current status: $($mysqlService.Status)"
} else {
    $mysqlServiceDetail = "MySQL service not found"
}
Show-Check "MySQL Service" ($mysqlService -and $mysqlService.Status -eq "Running") $mysqlServiceDetail

Write-Host ""
Write-Host "If all checks are [OK], run these commands in the project root:"
Write-Host "  cmake --preset windows-vcpkg"
Write-Host "  cmake --build --preset windows-vcpkg-debug"

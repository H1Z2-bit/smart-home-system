param(
    [string]$MysqlExe = "D:\MySQL\MySQL Server 8.0\bin\mysql.exe",
    [string]$User = "root",
    [string]$Password,
    [string]$SqlFile = "C:\Users\hanzhe\Desktop\software\smart_home.sql"
)

if (-not (Test-Path -LiteralPath $MysqlExe)) {
    throw "mysql.exe not found: $MysqlExe"
}

if (-not (Test-Path -LiteralPath $SqlFile)) {
    throw "SQL file not found: $SqlFile"
}

if (-not $Password) {
    $secure = Read-Host "Input MySQL password for user $User" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $Password = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

$previousMysqlPwd = $env:MYSQL_PWD
$env:MYSQL_PWD = $Password
try {
    Get-Content -LiteralPath $SqlFile -Raw -Encoding UTF8 |
        & $MysqlExe "-u$User" "--default-character-set=utf8mb4" "--binary-mode=1"
} finally {
    if ($null -eq $previousMysqlPwd) {
        Remove-Item Env:\MYSQL_PWD -ErrorAction SilentlyContinue
    } else {
        $env:MYSQL_PWD = $previousMysqlPwd
    }
}

if ($LASTEXITCODE -ne 0) {
    throw "MySQL schema import failed."
}

Write-Host "MySQL schema imported successfully."

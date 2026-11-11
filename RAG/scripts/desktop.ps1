[CmdletBinding()]
param(
    [ValidateSet('Start', 'Stop')][string]$Action = 'Start',
    [ValidateRange(1024, 65535)][int]$Port = 8090,
    [switch]$NoBrowser,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$env:PYTHONPATH = (Join-Path $projectRoot 'RAG') + $(if ($env:PYTHONPATH) { ';' + $env:PYTHONPATH } else { '' })
$instanceLock = $null
$created = @()
$state = $null
$statePath = $null

function Test-OwnedProcess($record) {
    if (-not $record) { return $false }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$record.id)" -ErrorAction SilentlyContinue
    return $process -and $process.CreationDate.ToUniversalTime().Ticks.ToString() -eq $record.created -and $process.CommandLine -eq $record.command
}

function Stop-OwnedProcess($record) {
    if (Test-OwnedProcess $record) {
        # PID, creation time and exact command must match before stopping its tree.
        & taskkill.exe /PID ([int]$record.id) /T /F 2>&1 | Out-Null
        if (Test-OwnedProcess $record) { throw '无法停止服务进程，请检查启动日志。' }
    }
}

function Start-ServiceProcess([string]$kind, [string[]]$arguments) {
    $stdout = Join-Path $logs ($kind + '.stdout.log')
    $stderr = Join-Path $logs ($kind + '.stderr.log')
    $quoted = @($arguments | ForEach-Object { '"' + $_ + '"' })
    $process = Start-Process -FilePath $python -ArgumentList $quoted -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $info = Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id)"
    if (-not $info) { throw "$kind 启动失败，请查看 $stderr" }
    return [pscustomobject]@{
        id = $process.Id
        created = $info.CreationDate.ToUniversalTime().Ticks.ToString()
        command = $info.CommandLine
    }
}

function Save-State {
    $temporary = $statePath + '.tmp'
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $statePath -Force
}

function Test-Ready([string]$url) {
    try {
        $response = Invoke-WebRequest -Uri ($url + 'health/live') -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch { return $false }
}

Push-Location -LiteralPath $projectRoot
try {
    if (-not (Test-Path -LiteralPath $python)) {
        throw '缺少 .venv Python 环境。请按 README 完成首次安装，再双击启动。'
    }
    $configuration = "import json, os; from pathlib import Path; from dotenv import load_dotenv; load_dotenv(); root = Path(os.getenv('RAG_SERVICE_DATA', 'storage')).resolve(); token = os.getenv('RAG_SERVICE_ADMIN_TOKEN') or ((root/'admin.token').read_text().strip() if (root/'admin.token').exists() else ''); print(json.dumps({'root': str(root), 'has_token': len(token) >= 24}))"
    $configText = & $python -c $configuration
    if ($LASTEXITCODE -ne 0) { throw 'Python 依赖不可用，请按 README 完成首次安装。' }
    $config = $configText | ConvertFrom-Json
    $dataRoot = $config.root
    $logs = Join-Path $dataRoot 'logs'
    New-Item -ItemType Directory -Path $logs -Force | Out-Null
    $statePath = Join-Path $dataRoot 'desktop.json'
    try {
        $instanceLock = [IO.File]::Open((Join-Path $dataRoot 'desktop.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
    } catch { throw '另一个启动或停止操作正在进行，请稍后重试。' }
    if (Test-Path -LiteralPath $statePath) {
        $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($state.project -ne $projectRoot -or $state.data -ne $dataRoot) {
            throw '启动记录属于其他目录，未操作任何进程，请检查数据目录设置。'
        }
    }
    if ($Action -eq 'Stop') {
        if ($state) {
            Stop-OwnedProcess $state.worker
            Stop-OwnedProcess $state.server
            Remove-Item -LiteralPath $statePath
        }
        Write-Output '知识服务已停止。'
    } else {
        if (-not $config.has_token -or -not (Test-Path -LiteralPath (Join-Path $dataRoot 'catalog.sqlite3'))) {
            & $python -m app --data $dataRoot init *> (Join-Path $logs 'initialize.log')
            if ($LASTEXITCODE -ne 0) { throw "初始化失败，请查看 $logs\initialize.log" }
        }
        if ($state -and (Test-OwnedProcess $state.server) -and $state.server.command -notmatch '--local-console') {
            Stop-OwnedProcess $state.server
        }
        if ($state -and (Test-OwnedProcess $state.server)) {
            $url = $state.url
        } else {
            if ($state) { Stop-OwnedProcess $state.worker }
            $url = "http://127.0.0.1:$Port/"
            if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
                throw "端口 $Port 已被占用，未关闭或接管其他进程。请先停止此前手工启动的服务。"
            }
            $state = [pscustomobject]@{ project = $projectRoot; data = $dataRoot; url = $url; server = $null; worker = $null }
            $state.server = Start-ServiceProcess 'server' @('-m', 'app', '--data', $dataRoot, 'serve', '--host', '127.0.0.1', '--port', "$Port", '--local-console')
            $created += $state.server
            Save-State
        }
        $deadline = [DateTime]::UtcNow.AddSeconds(60)
        while (-not (Test-Ready $url)) {
            if (-not (Test-OwnedProcess $state.server) -or [DateTime]::UtcNow -gt $deadline) {
                throw "网页服务未能就绪，请查看 $logs\server.stderr.log"
            }
            Start-Sleep -Milliseconds 400
        }
        if (-not (Test-OwnedProcess $state.worker)) {
            # A manual worker holding this lock is left alone; never create a duplicate.
            $workerLock = $null
            try {
                $workerLock = [IO.File]::Open((Join-Path $dataRoot 'worker.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
            } catch { throw '已有手工启动的 Worker。请先停止它，再使用双击启动统一管理。' }
            finally { if ($workerLock) { $workerLock.Dispose() } }
            $workerReady = Join-Path $dataRoot 'desktop-worker-ready'
            Remove-Item -LiteralPath $workerReady -ErrorAction SilentlyContinue
            $state.worker = Start-ServiceProcess 'worker' @('-m', 'app', '--data', $dataRoot, 'worker', '--desktop-safe-start')
            $created += $state.worker
            Save-State
            $deadline = [DateTime]::UtcNow.AddSeconds(60)
            while (-not (Test-Path -LiteralPath $workerReady)) {
                if (-not (Test-OwnedProcess $state.worker) -or [DateTime]::UtcNow -gt $deadline) {
                    throw "后台处理程序未能就绪，请查看 $logs\worker.stderr.log"
                }
                Start-Sleep -Milliseconds 400
            }
        }
        Save-State
        if (-not $NoBrowser) { Start-Process $url }
        Write-Output "知识服务已启动：$url"
    }
} catch {
    $message = $_.Exception.Message
    foreach ($record in $created) {
        try { Stop-OwnedProcess $record } catch { }
    }
    if ($statePath -and $state -and -not (Test-OwnedProcess $state.server) -and -not (Test-OwnedProcess $state.worker)) {
        Remove-Item -LiteralPath $statePath -ErrorAction SilentlyContinue
    }
    if (-not $Quiet) {
        Add-Type -AssemblyName System.Windows.Forms
        [Windows.Forms.MessageBox]::Show($message, '知序启动 / 停止', 'OK', 'Error') | Out-Null
    }
    Write-Error $message -ErrorAction Continue
    exit 1
} finally {
    if ($instanceLock) { $instanceLock.Dispose() }
    Pop-Location
}

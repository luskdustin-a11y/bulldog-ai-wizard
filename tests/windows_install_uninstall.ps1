# Real silent install/uninstall smoke test on GitHub-hosted Windows.
$ErrorActionPreference = 'Stop'
$installer = (Resolve-Path 'output/Archie-Light-Setup.exe').Path
$target = Join-Path $env:RUNNER_TEMP 'ArchieLightAcceptance'
$log = Join-Path $env:RUNNER_TEMP 'archie-install.log'
if (Test-Path $target) { throw "Test install directory already exists: $target" }
$install = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=$target", "/LOG=$log") -Wait -PassThru
if ($install.ExitCode -ne 0) { throw "Install failed: $($install.ExitCode)" }
$exe = Join-Path $target 'ARCHER.exe'
$ollama = Join-Path $target 'ollama\ollama.exe'
if (!(Test-Path $exe)) { throw 'Installed Archie executable missing' }
if (!(Test-Path $ollama)) { throw 'Installed Ollama executable missing' }
$sim = & $exe --simulate | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $sim.passed -ne 8 -or $sim.total -ne 8) { throw 'Installed Archie simulator failed' }
$uninstaller = Join-Path $target 'unins000.exe'
if (!(Test-Path $uninstaller)) { throw 'Uninstaller missing' }
$remove = Start-Process -FilePath $uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -Wait -PassThru
if ($remove.ExitCode -ne 0) { throw "Uninstall failed: $($remove.ExitCode)" }
if (Test-Path $exe) { throw 'Archie executable remains after uninstall' }
if (Test-Path $ollama) { throw 'Ollama executable remains after uninstall' }
Write-Host 'PASS: real Windows install, packaged executable smoke test, and uninstall'

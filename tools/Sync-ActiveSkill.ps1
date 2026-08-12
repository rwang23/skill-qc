[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Destination,

    [switch]$VerifyOnly
)

$ErrorActionPreference = 'Stop'

$sourceRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$destinationRoot = [IO.Path]::GetFullPath($Destination)

if ($destinationRoot.TrimEnd('\') -eq $sourceRoot.TrimEnd('\')) {
    throw 'Destination must be a runtime mirror, not the canonical source repository.'
}

$packageFiles = @(
    'SKILL.md',
    'agents\openai.yaml',
    'assets\report-template.en.html',
    'assets\report-template.zh-CN.html',
    'evals\evals.json',
    'references\evidence-schema.md',
    'references\report-contract.md',
    'references\review-protocol.md',
    'references\rubric.md',
    'scripts\skill_audit.py'
)

if (-not $VerifyOnly) {
    [IO.Directory]::CreateDirectory($destinationRoot) | Out-Null
    foreach ($relativePath in $packageFiles) {
        $sourcePath = Join-Path $sourceRoot $relativePath
        $destinationPath = Join-Path $destinationRoot $relativePath
        [IO.Directory]::CreateDirectory((Split-Path -Parent $destinationPath)) | Out-Null
        Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Force
    }
}

if (-not (Test-Path -LiteralPath $destinationRoot -PathType Container)) {
    throw "Runtime mirror does not exist: $destinationRoot"
}

$issues = [System.Collections.Generic.List[string]]::new()
foreach ($relativePath in $packageFiles) {
    $sourcePath = Join-Path $sourceRoot $relativePath
    $destinationPath = Join-Path $destinationRoot $relativePath
    if (-not (Test-Path -LiteralPath $destinationPath -PathType Leaf)) {
        $issues.Add("missing: $relativePath")
        continue
    }
    $sourceHash = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
    $destinationHash = (Get-FileHash -LiteralPath $destinationPath -Algorithm SHA256).Hash
    if ($sourceHash -ne $destinationHash) {
        $issues.Add("hash-mismatch: $relativePath")
    }
}

$expected = @($packageFiles | ForEach-Object { $_.Replace('\', '/').ToLowerInvariant() })
$actual = @(
    Get-ChildItem -LiteralPath $destinationRoot -Recurse -File |
        ForEach-Object {
            [IO.Path]::GetRelativePath($destinationRoot, $_.FullName).Replace('\', '/').ToLowerInvariant()
        }
)
foreach ($relativePath in $actual) {
    if ($relativePath -notin $expected) {
        $issues.Add("unexpected: $relativePath")
    }
}

if ($issues.Count -gt 0) {
    $issues | ForEach-Object { Write-Error $_ }
    exit 1
}

$mode = if ($VerifyOnly) { 'verify' } else { 'apply' }
Write-Output "Sync-ActiveSkill: mode=$mode files=$($packageFiles.Count) status=PASS destination=$destinationRoot"

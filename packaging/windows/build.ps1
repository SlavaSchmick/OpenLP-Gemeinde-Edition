# OpenLP - Windows build
#
# Builds OpenLP.exe with PyInstaller, adds the OpenLP files, translations and VLC, and creates the installer with
# Inno Setup. Run it from the repository root:
#
#     powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
#
# Requirements: the virtual environment in .venv with PyInstaller, VLC (64 bit) and Inno Setup 6.
param(
    [string]$VlcDir = 'C:\Program Files\VideoLAN\VLC',
    [string]$InnoSetup = ''
)
$ErrorActionPreference = 'Stop'

$repo = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$here = $PSScriptRoot
$python = Join-Path $repo '.venv\Scripts\python.exe'
$work = Join-Path $here 'build'
$dist = Join-Path $here 'dist'
$app = Join-Path $dist 'OpenLP'
$version = (Get-Content (Join-Path $repo 'openlp\.version') -Raw).Trim()

if (-not $InnoSetup) {
    $InnoSetup = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
                   "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
                   "$env:ProgramFiles\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $InnoSetup) { throw 'Inno Setup 6 (ISCC.exe) not found' }
if (-not (Test-Path (Join-Path $VlcDir 'libvlc.dll'))) { throw "VLC not found in $VlcDir" }

# The edition (a modified version of OpenLP) and its GitHub repository, see openlp/core/edition.py
$editionSource = Get-Content (Join-Path $repo 'openlp\core\edition.py') -Raw
$edition = [regex]::Match($editionSource, "EDITION_NAME = '([^']*)'").Groups[1].Value
$repository = [regex]::Match($editionSource, "EDITION_REPOSITORY = '([^']*)'").Groups[1].Value
$productName = "OpenLP $edition"
$repositoryUrl = if ($repository) { "https://github.com/$repository" } else { 'https://openlp.org/' }

Write-Host "== $productName $version"

# Version resource of OpenLP.exe; a version like "3.1.7+gemeinde.1" becomes 3.1.7.1
$info = Join-Path $here 'build-info'
New-Item -ItemType Directory -Force $info | Out-Null
$numbers = ($version -split '[^0-9]+' | Where-Object { $_ } | Select-Object -First 4)
while ($numbers.Count -lt 4) { $numbers += '0' }
$tuple = $numbers -join ', '
$numericVersion = $numbers -join '.'
# For file names, e.g. "3.1.7-gemeinde.1"
$fileVersion = $version -replace '\+', '-'
$versionInfo = @"
VSVersionInfo(
  ffi=FixedFileInfo(filevers=($tuple), prodvers=($tuple), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1,
                    subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', '$productName (modified OpenLP)'),
      StringStruct('FileDescription', '$productName - modified version of OpenLP'),
      StringStruct('FileVersion', '$version'),
      StringStruct('InternalName', 'OpenLP'),
      StringStruct('LegalCopyright', 'Copyright (c) 2008-2024 OpenLP Developers, GPL 3; modified'),
      StringStruct('OriginalFilename', 'OpenLP.exe'),
      StringStruct('ProductName', '$productName'),
      StringStruct('ProductVersion', '$version')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"@
# Without a byte order mark, which PyInstaller can't read
[IO.File]::WriteAllText((Join-Path $info 'version_info.txt'), $versionInfo, (New-Object Text.UTF8Encoding $false))

Write-Host '== PyInstaller'
& $python -m PyInstaller --noconfirm --clean --workpath $work --distpath $dist (Join-Path $here 'openlp.spec')
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }

Write-Host '== OpenLP files'
# OpenLP finds plugins, display pages, fonts and theme files by their path next to OpenLP.exe
$source = Join-Path $repo 'openlp'
Get-ChildItem $source -Recurse -File | Where-Object {
    $_.FullName -notmatch '\\__pycache__\\' -and $_.Extension -ne '.pyc'
} | ForEach-Object {
    $target = Join-Path $app $_.FullName.Substring($source.Length + 1)
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    Copy-Item $_.FullName $target -Force
}

Write-Host '== Translations'
$i18n = Join-Path $app 'i18n'
New-Item -ItemType Directory -Force $i18n | Out-Null
$lrelease = Get-ChildItem (Join-Path $repo '.venv') -Recurse -Filter lrelease.exe | Select-Object -First 1
foreach ($language in 'de', 'ru', 'uk') {
    & $lrelease.FullName (Join-Path $repo "resources\i18n\$language.ts") -qm (Join-Path $i18n "$language.qm") | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "lrelease failed for $language" }
}

Write-Host '== VLC'
$vlc = Join-Path $app 'vlc'
New-Item -ItemType Directory -Force $vlc | Out-Null
Copy-Item (Join-Path $VlcDir 'libvlc.dll'), (Join-Path $VlcDir 'libvlccore.dll') $vlc -Force
Copy-Item (Join-Path $VlcDir 'plugins') $vlc -Recurse -Force
foreach ($file in 'COPYING.txt', 'AUTHORS.txt') {
    if (Test-Path (Join-Path $VlcDir $file)) { Copy-Item (Join-Path $VlcDir $file) (Join-Path $vlc $file) -Force }
}
Copy-Item (Join-Path $repo 'LICENSE') (Join-Path $app 'LICENSE.txt') -Force

Write-Host '== Installer'
& $InnoSetup "/DAppVersion=$version" "/DAppVersionNumeric=$numericVersion" "/DAppFileVersion=$fileVersion" `
    "/DProductName=$productName" "/DProductUrl=$repositoryUrl" "/DSourceDir=$app" "/DRepoDir=$repo" `
    "/O$(Join-Path $here 'output')" (Join-Path $here 'openlp.iss')
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup failed' }
Write-Host "== Done: $(Join-Path $here 'output')"
